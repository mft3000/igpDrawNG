#### igpDrawNGv2.py / base.html

Takes LSA 1 and LSA 2 as input (from 'show ip ospf database router | network') in order to produce <topology>.js filename witch stores JS variable that will be read from base.html (based on Cisco Next UI framework)

#### Tasks

+ DONE

```

	python

		- resolution hostname
			- NS resolution
			- SNMP resolution ( community by env var or hardcoded )
			- no resolution (--offline)
		- filter inclusive (hostname or ip) with regexp

	nextui

		- browse and load topology
		- change hostname at the fly (bidir)
		
		shows:
		- 1x P2P same cost
		- 1x P2P different cost
		- 1x BCAST same cost m2p
		- 1x BCAST same different m2p
		- 1x BCAST same cost p2p (optimize)
		- 1x BCAST same different p2p (optimize)

```

+ TODO

```

	wait for igpDrawNG for 
	- igpDrawNGv2.js
	- save modified topology as new filename
	- determine path strict nexthops (for MPLS TE explicit paths)
	- hide nodes
	- talk with Cisco Network Services Orchestrator (NSO - ex tail-f) as Northbound API REST (trigger NSO services, execute commands etc...)
	- etc...
	
```

manual procedure 

```
(Dev)fmarangione (master *) igpDrawNG $ python igpDrawNGv2.py -r 2.network.r.db -n 3.network.n.db --offline
INFO:root: +++++ read LSA 2 +++++
INFO:root:3.network.n.db
INFO:root: +++++ read LSA 1 +++++
INFO:root:2.network.r.db
2.2.2.2
7.7.7.7
8.8.8.8
9.9.9.9
10.10.10.10
11.11.11.11
12.12.12.12
13.13.13.13
14.14.14.14
19.19.19.19
```

![alt tag](https://github.com/mft3000/igpDrawNG/blob/master/5.network.png)

examples with filters

```
python igpDrawNG.py -f 47.1.103.2 47.1.103.3 48.96.22.209 48.2.141.208 48.2.144.215 48.2.154.214 35.3.50.42 35.3.50.41 35.3.50.48

python igpDrawNG.py -f pe p asbr
```

filtrer -f regexp

```
python igpDrawNGv2.py -r 2.network.r.db -n 3.network.n.db

python igpDrawNGv2.py -r 2.network.r.db -n 3.network.n.db -f .*-p00[12] milan-.*-p10[12]
```