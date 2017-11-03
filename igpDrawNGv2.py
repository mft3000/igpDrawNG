#!/usr/bin/env python

########### version 0.562
#
# 0.56: init script
# 0.562: add regexp inside include filter
#
###########

import re, argparse, os, json, socket

import ipcalc

# from snimpy.manager import Manager as M
# from snimpy.manager import load

from scapy.all import SNMP, SNMPget, SNMPvarbind, DNS, DNSQR

# ++++++++++++++++++++
import logging
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)
# --------------------

try:
	snmpcomm = os.environ["PYCOMM"]
except:
	snmpcomm = 'public'

def isIPADDRESS(obj):
	if re.match('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', obj):
		return True
	else:
		return False

def stripAfterDot(var):
	try:
		ix = var.index('.')
		return var[:ix]
	except:
		return var

def get_resolvers():
	resolvers = []
	try:
		with open( '/etc/resolv.conf', 'r' ) as resolvconf:
			for line in resolvconf.readlines():
				line = line.split( '#', 1 )[ 0 ];
				line = line.rstrip();
				if 'nameserver' in line:
					resolvers.append( line.split()[ 1 ] )
		return resolvers
	except IOError as error:
		return error.strerror
		
def resolveIPtoNAME(ipaddress):

	if re.match('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', ipaddress):

		name = ''.join(socket.gethostbyaddr(ipaddress)[0])
		return stripAfterDot(name)
				
def resolveIPtoNAMEwithScapy(ipaddress):

	if re.match('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', ipaddress):
		
		resolve = get_resolvers()[0]
		
		ip = ipaddress.split('.')
		ip.reverse()
		target_resolve = '.'.join(ip) + ".in-addr.arpa"

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.connect((resolve, 53))
		sock.settimeout(0.2)
		
		dns = DNS(rd = 1, qd = DNSQR(qname=target_resolve, qtype='PTR'))
		buf = str( dns )
		while buf:
			bytes = sock.send( buf )
			buf = buf[bytes:]

		response = DNS( sock.recv(4096) )
		# print response.show()
		answer = response["DNS"].an.rdata[:-1]
		return stripAfterDot( answer )

class Router(object):
		def __init__(self, rid):
			# rid
			self.routerid = rid
			# hostname
			self.hostname = rid
			# ip, subnet, cost
			self.stubs = []
			# neigh RID, myIPaddress cost
			self.link = []
			# neigh in broadcast segment network
			self.transits = []

		def __str__(self):
			return self.hostname + ' (' + self.routerid + ')' + '\n '

		def resolveIPtoNAMEFromSNMP(self, ipaddress, comm = str(snmpcomm)):

			logging.info(ipaddress)
			logging.info(comm)
			result = None

			try:

				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sock.connect((ipaddress, 161))
				sock.settimeout(0.2)

				snmp = SNMP( community=comm, PDU=SNMPget(varbindlist=[SNMPvarbind(oid="1.3.6.1.2.1.1.5.0")]) )
				# print snmp.show()
				buf = str( snmp )
				while buf:
					bytes = sock.send( buf )
					buf = buf[bytes:]

				response = SNMP( sock.recv(4096) )
				# response.show()
				result = stripAfterDot( response[SNMPvarbind].value.val )
				sock.close()

				# load("RFC1213-MIB")
				# m = M(ipaddress, comm, version=2, none=True, timeout=0.1)
				#
				# result = stripAfterDot(m.sysName)

				return True, result
			#
			except:
				return False, ipaddress

		def sethostname(self, target, translate = True):

			if isIPADDRESS(target):
				if translate:
					try:
						# dns resolve	
						print
						logging.info('+++ dns resolve +++')
						self.hostname = resolveIPtoNAME(target)
						logging.info(self.hostname)
						logging.info('--- dns resolve ---')
						
					except:
						try:
							logging.info('+++ snmp resolve +++')
							r, self.hostname = self.resolveIPtoNAMEFromSNMP(target)
							logging.info(r)
							logging.info(self.hostname)
							logging.info('--- snmp resolve ---')
						except:
								# if fail ns and snmp
								self.hostname = target
				else:
						self.hostname = target
			else:
					self.hostname = target

		def addstub(self, subnet, mask, metric):
			self.stubs.append([subnet, mask, metric])

		def addlink(self, neighbour, ip, metric, type = 'P2P'):
			self.link.append([neighbour, ip, metric, type])

		def addtransit(self, dr, myintip, metric, type = 'BCAST'):
			self.transits.append([dr, myintip, metric, type])

		def addtransitASnode(self, rid, subnet, cost = 0, type = 'BCAST'):
			self.transits.append([rid, subnet, cost, type])

		def build_nodes(self, id = 0):
			return { "id": id, "name": self.hostname, "rid": self.routerid, "icon": "router", "adj": self.link, "stubs": self.stubs, "x": "null", "y": "null", "status": "up", "longitude": "null", "latitude": "null" }

		def build_links(self, start = 0, end = 0, cost = 0, visible = True, dotten = 'True', color = 'light-blue', net_sm_link = None, width = 0):
			return { "source": start, "target": end, "cost": cost, "visible": visible, "color": color, "net_sm_link": net_sm_link, "width": width}

		def build_transit(self, id = 0, subnet = '0.0.0.0', dr = '0.0.0.0'):
			return { "id": id, "subnet": subnet, "dr": dr, "icon":"unknown", "color":"red" }

class OSPF(object):

	# delimiter = ':'
	pid = ''
	file_rid = ''
	area = ''
	router_file = ''
	network_file = ''
	output_file = ''
	routers = []
	transits = []

	nodes = []
	links = []

	topologyData = {}

	optimize_DR_list = []

	def __init__(self, router_file = '', network_file = '', offline = False, translate = True, output_file = '', include_filter_topology = [], exclude_filter_topology = [], nodeset = []):

		self.router_file = router_file
		self.network_file = network_file
		self.output_file = output_file

		self._read_network_database_file(offline, translate)
		self._read_router_database_file(offline, translate)

		# self.read_parameters()

		for ixr, r in enumerate( self.routers ):

			# print
			print r.hostname
			# print r.stubs
			# print r.link

			if include_filter_topology:
				'''
				include filter results based on partition of hostname.
				'''
				for include_filter in include_filter_topology:
					if isIPADDRESS(include_filter):
						if include_filter in r.routerid:
							self.build_js_topology(r, ixr)
					else:
						if include_filter in r.hostname:
							self.build_js_topology(r, ixr)
						elif re.match(include_filter, r.hostname):
							self.build_js_topology(r, ixr)
							
			elif nodeset:
				for nodeset_input in nodeset:
					if isIPADDRESS(nodeset_input):
						if nodeset_input == r.routerid:
							self._build_nodesets(nodeset_input)
					else:
						if nodeset_input in r.hostname:
							self._build_nodesets(nodeset_input)

				self.build_js_topology(r, ixr)

			else:
				self.build_js_topology(r, ixr)

		self._build_topology_file( )

	def _netmask_full_to_short(self, netmask):
		return sum([bin(int(x)).count("1") for x in netmask.split(".")])

	def _build_nodesets(n):
		# self.target2Index = lambda x: [ ix for ix, r in enumerate( self.routers ) if r.routerid == x ][0]

		nodeSet[0]["nodes"].append( self.target2Index(n) )

	def read_parameters(self):
		print
		print 'OSPF PID: ', self.pid
		print 'OSPF RID: ', self.file_rid
		print 'OSPF AREA: ', self.area

	def _read_router_database_file(self, offline = False, translate = True):

		neighbour = None
		stubnet = None
		transit = None

		logging.info(' +++++ read LSA 1 +++++ ')
		logging.info(self.router_file)

		with open(self.router_file) as file:
			for line in file:
				line = line.rstrip()

				m = re.search('OSPF Router with ID \((\d*.\d*.\d*.\d*)\) \(Process ID (\d*)\)', line)
				if m:
					self.file_rid = m.group(1)
					self.pid = m.group(2)

				m = re.search('Router Link States \(Area (\d*)\)', line)
				if m:
					self.area = m.group(1)

				###### Link State ID
				m = re.search('Link State ID: (\d*.\d*.\d*.\d*)', line)
				if m:
					rtr = Router( m.group(1) )
					self.routers.append( rtr )

				###### Advertising Router
				m = re.search('Advertising Router: (\S*)', line)
				if m:
					if offline:
						rtr.sethostname(m.group(1), translate = False)
					else:
						rtr.sethostname(m.group(1), translate = translate)

				###### Link ID Network/subnet number:                           network to announce
				m = re.search('\(Link ID\) Network/subnet number: (\d*.\d*.\d*.\d*)', line)
				if m:
					stubnet = m.group(1)

				###### Link Data Network Mask:                                  subnet/network to announce
				m = re.search('\(Link Data\) Network Mask: (\d*.\d*.\d*.\d*)', line)
				if m:
					stubmask = m.group(1)

				###### Link ID Neighboring Router ID:                           neighbor RID
				m = re.search('\(Link ID\) Neighboring Router ID: (\d*.\d*.\d*.\d*)', line)
				if m:
					neighbour = m.group(1)

				###### Link Data Router Interface address:                      router ip address where I learn neighbor RID
				m = re.search('\(Link Data\) Router Interface address: (\d*.\d*.\d*.\d*)', line)
				if m:
					interfaceip = m.group(1)

				###### Link Data Router Interface address
				m = re.search('\(Link ID\) Designated Router address: (\d*.\d*.\d*.\d*)', line)
				if m:
					transit = m.group(1)

				###### TOS 0 Metrics
				m = re.search('TOS 0 Metrics: (\d*)', line)
				if m:
					if neighbour is not None:
						rtr.addlink(neighbour, interfaceip, m.group(1))
						neighbour = None
						interfaceip = None
					elif stubnet is not None:
						rtr.addstub(stubnet, stubmask, m.group(1))
						stubnet = None
						stubmask = None
					elif transit is not None:
						if(transit not in self.transits):
							self.transits.append(transit)
						rtr.addtransit(transit, interfaceip, m.group(1))
						# even add as simple link to show summary neighbour in NEXT UI
						rtr.addlink(transit, interfaceip, m.group(1), 'BCAST')
						transit = None

				# if self.delimiter in line:
					# # name = "".join(line.split()[0])
					# print line.split(self.delimiter)[0], ':', line.split(self.delimiter)[1]

	def _read_network_database_file(self, offline = False, translate = True):

		neighbour = None

		logging.info(' +++++ read LSA 2 +++++ ')
		logging.info(self.network_file)

		with open(self.network_file) as file:
			for line in file:
				line = line.rstrip()
				# print line

				###### Link State ID
				m = re.search('Link State ID: (\d*.\d*.\d*.\d*) \(address of Designated Router\)', line)
				if m:
					rtr = Router( m.group(1) )
					# rtr.sethostname( m.group(1), translate = False )
					self.routers.append( rtr )

				###### Advertising Router
				# m = re.search('Advertising Router: (\S*)', line)
				# if m:
				# 	if offline:
				# 		rtr.sethostname(m.group(1), translate = False)
				# 	else:
				# 		rtr.sethostname(m.group(1), translate = translate)

				###### Network Mask
				m = re.search('Network Mask: (\S*)', line)
				if m:
					subnetMask = m.group(1)
					transit_name = str(ipcalc.Network(rtr.routerid + subnetMask).network()) + subnetMask
					rtr.sethostname( transit_name, translate = False )

				###### Attached Router: Routers RID list of attached devices to this LAN segment
				m = re.search('Attached Router: (\d*.\d*.\d*.\d*)', line)
				if m:
					rtr.addtransitASnode( m.group(1), transit_name, 0 )

	def _find_net_sm_from_stubs(self, r, ip):
		for ns in r.stubs:
			net = ns[0] + '/' + str( self._netmask_full_to_short( ns[1] ) )
			if ip in ipcalc.Network(net):
				return net

	# def _check_if_exist_transit_list(self, t, d):
	#
	# 		for x in d:
	# 			try:
	# 				if x['dr'] == t:
	# 						# print '-', x
	# 						return False
	# 			except:
	# 				continue
	# 		return True

	# def _if_exist_reverse_path_with_same_cost(self, s, t, c, d):
	#
	# 		for x in d:
	# 				if x['source'] == t and x['target'] == s and x['cost'] == c:
	# 						# print '-', x
	# 						return False
	#
	# 		return True

	def target2Index(self, x):

		for ix, r in enumerate( self.routers ):
				if r.routerid == x:
					return ix

	def build_js_topology(self, r, ixr):

		self.nodes.append( r.build_nodes(ixr) )

		##### p2p
		for ixl, lnk in enumerate( r.link ):

			target = self.target2Index( lnk[0] )

			############
			net_sm = self._find_net_sm_from_stubs(r, lnk[1])
			self.links.append( r.build_links( start = ixr, end = target, cost = int(lnk[2]), visible = True, net_sm_link = net_sm ) )

			############
			# if self._if_exist_reverse_path_with_same_cost(ixr, target, int(lnk[2]), links):
			#
			# 		net_sm = _find_net_sm_from_stubs(r, lnk[1])
			#
			# 		links.append( r.build_links( ixr, target, int(lnk[2]), visible = True, net_sm_link = net_sm ) )
			# else:
			# 		links.append( r.build_links( ixr, target, int(lnk[2]), visible = False ) )

		netsm = None
		##### bcast
		for ixt, tnsit in enumerate( r.transits ):
			# print r.routerid
			# print tnsit
			# idtemp = (len(self.nodes) + 1)
			# if self._check_if_exist_transit_list(tnsit[0], self.nodes):
			# 	self.nodes.append( r.build_transit( idtemp, dr = tnsit[0]) )
			# target = self.target2Index( r.routerid )
			# self.links.append( r.build_links( idtemp, target, int(tnsit[2]), visible = True, dotten = True ) )

			# print r.routerid
			print tnsit
			head, tail, netsm, cost = self.target2Index( r.routerid ), self.target2Index( tnsit[0] ), tnsit[1], int(tnsit[2])
			self.links.append( r.build_links( start = head, end = tail, cost = cost, visible = True, dotten = True ) )
			self.optimize_DR_list.append( tnsit[0] )

		if netsm: self._optimize_p2p_with_DR( net_slash_sm = tnsit[1] )
		self.optimize_DR_list = []

	def _optimize_p2p_with_DR(self, net_slash_sm):

		# target2Index = lambda x: [ ix for ix, r in enumerate( self.routers ) if r.routerid == x ][0]
		####### optimize BCAST LAN segments
		node_to_remove = None
		if len(list(set(self.optimize_DR_list))) == 2:
			print
			print 'optimize:', len(list(set(self.optimize_DR_list)))
			print net_slash_sm
			print list(set(self.optimize_DR_list))
			print
			print '+', self.optimize_DR_list[0]
			print self.routers[self.target2Index( self.optimize_DR_list[0] )].link
			for l in self.routers[self.target2Index( self.optimize_DR_list[0] )].link:
				if l[0] in ipcalc.Network(net_slash_sm):
					print l[0], ' in ', net_slash_sm
					node_to_remove = l[0]
					l[0] = self.optimize_DR_list[1]
					print 'new', l

			print '+', self.optimize_DR_list[1]
			print self.routers[self.target2Index( self.optimize_DR_list[1] )].link
			for l in self.routers[self.target2Index( self.optimize_DR_list[1] )].link:
				if l[0] in ipcalc.Network( net_slash_sm ):
					print l[0], ' in ', net_slash_sm
					l[0] = self.optimize_DR_list[0]
					print 'new', l

			print
			print 'delete node'

			for ix, r in enumerate(self.nodes):
				if r['rid'] == node_to_remove:
					print r['rid']
					self.nodes.pop()
				# if r.routerid == node_to_remove:
				# 	print ix, r.routerid
				# 	self.nodes.pop(ix)
				# else:
				# 	print r.routerid

			print 'end optimization'
			print

	def _build_topology_file(self):

		# self.topologyData  = { 'links': self.links }
		# self.topologyData  = { 'nodes': self.nodes }
		self.topologyData  = { 'nodes': self.nodes, 'links': self.links }
		# self.topologyData  = { 'nodes': self.nodes, 'links': self.links, 'nodeSet': self.nodeSet }

		# print self.topologyData
		# print json.dumps(self.topologyData , sort_keys=False, indent=4, separators=(',', ': '))

		self._write_json( )

	def _write_json(self, target_dir = './'):

		out_file_name_json = open(target_dir + self.output_file + ".js", "w")
		out_file_name_json.write("var topologyData = ")
		print >> out_file_name_json, json.dumps( self.topologyData, sort_keys=False, indent=4, separators=(',', ': ') )
		out_file_name_json.write(";")
		out_file_name_json.close()


def main():

	parser = argparse.ArgumentParser(description='')

	parser.add_argument('-r','--router', default='lab.r.db')
	parser.add_argument('-n','--network', default='lab.n.db')
	parser.add_argument('-o','--output', default='area0')

	parser.add_argument('--offline', action='store_true', default=False)
	parser.add_argument('-t','--translate', action='store_true', default=True)

	parser.add_argument('-f','--include', nargs='+', default=[])
	parser.add_argument('-e','--exclude', nargs='+', default=[])

	parser.add_argument('--nodeset', nargs='+', default=[])
	# parser.add_argument('-c','--community', default='')

	args = parser.parse_args()

	######################################################################

	o = OSPF(	router_file = args.router,
				network_file = args.network,
				offline = args.offline,
				translate = args.translate,
				output_file = args.output,
				include_filter_topology = args.include,
				exclude_filter_topology = args.exclude,
				nodeset = args.nodeset )

if __name__ == '__main__':
		main()
