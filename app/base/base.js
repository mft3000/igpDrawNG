// ver 0.1 

// NextUI igpDrawNGv2.py reader 
// Francesco Marangione (fmarangi@cisco.com) 

nx.define('Search', nx.ui.Component, {
  view: {
    content: [
      {
        tag: 'input',
        props: {
          value: '{#nodeSearch}'
        }
      },
      {
        tag: 'p',
        content: [
          {
            tag: 'span',
            content: 'Search '
          },
          {
            tag: 'span',
            content: '{#nodeSearch}'
          }
        ]
      }
    ]
  },
  properties: {
    nodeSearch: ''
  }
});

nx.define('showSelfOriginate', nx.ui.Component, {
    properties: {
        node: {},
        topology: {}
    },
    view: {
        content: [
         {
            tag: "table",
            props: {
                class: "col-md-12",
                border: "1"
            },
            content: [{
                tag: "thead",
                content: {
                    tag: "tr",
                    content: [{
                        tag: "td",
                        content: "Network"
                    }, {
                        tag: "td",
                        content: "Subnet"
                    }, {
                        tag: "td",
                        content: "Cost"
                    }]
                }
            }, {
                tag: "tbody",
                props: {
                    items: "{#node.model.stubs}",
                    template: {
                        tag: "tr",
                        content: [{
                            tag: "td",
                            content: "{0}"
                        }, {
                            tag: "td",
                            content: "{1}"
                        }, {
                            tag: "td",
                            content: "{2}"
                        }]
                    }
                }
            }]
        }]
      }
});

nx.define('showNeighbor', nx.ui.Component, {
    properties: {
        node: {},
        topology: {}
    },
    view: {
        content: [{
            tag: "table",
            props: {
                class: "col-md-12",
                border: "1"
            },
            content: [{
                tag: "thead",
                content: {
                    tag: "tr",
                    content: [{
                        tag: "td",
                        content: "Adj RID"
                    }, {
                        tag: "td",
                        content: "myIPaddress"
                    }, {
                        tag: "td",
                        content: "Cost"
                    }]
                }
            }, {
                tag: "tbody",
                props: {
                    items: "{#node.model.adj}",
                    template: {
                        tag: "tr",
                        content: [{
                            tag: "td",
                            content: "{0}"
                        }, {
                            tag: "td",
                            content: "{1}"
                        }, {
                            tag: "td",
                            content: "{2}"
                        }]
                  }
              }
          }]
      }]
    }
});

nx.define('MyNodeTooltip', nx.ui.Component, {
    properties: {
        node: {},
        topology: {}
    },
    view: {
        content: [
		{
            tag: 'p',
            content: [{
                tag: 'label',
                content: 'id: '
            }, {
                tag: 'span',
                content: '{#node.id}'
            }]
        }, {
			tag: 'h3',
			content: [{
				tag: 'table',
				content: [{
					tag: 'tr',
					content: [{
						tag: 'th',
						content: [{
							tag: 'label',
							content: 'Hostname:'
						}]
					}, {
						tag: 'th',
						content: [{
							tag: 'input',
							props: {
									value: '{#node.model.name}',
									id: 'EditedHostname',
									size: "15",
									maxlength: "30"
							}
						}]
					}]
				}]
			}]       
		}, {
			tag: 'h3',
			content: [{
				tag: 'table',
				content: [{
					tag: 'tr',
					content: [{
						tag: 'th',
						content: [{
							tag: 'label',
							content: 'Ospf RID:'
						}]
					}, {
						tag: 'th',
						content: [{
							tag: 'span',
							content: '{#node.model.rid}'
						}]
					}]
				}]
			}]       
		}, {
                tag: 'button',
                props: {
                    type: 'button',
                    'class': 'btn btn-default'
                },
                content: 'Neighbor',
                events: {
                    'click': '{#_show_neighbors}'
                }
        }, {
                  tag: 'button',
                  props: {
                      type: 'button',
                      'class': 'btn btn-default'
                  },
                  content: 'SelfOriginate',
                  events: {
                      'click': '{#_show_self_originate}'
                  }
        }

      ],
    },
    methods: {
        _show_neighbors: function() {
            var sn = new showNeighbor();
            sn.attach( this );
            sn.node( this.node() );
        },
        _show_self_originate: function() {
            var sso = new showSelfOriginate();
            sso.attach( this );
            sso.node( this.node() );
        }
    }
});

nx.define('MyLinkTooltip', nx.ui.Component, {
    properties: {
        link: {},
        topology: {}
    },
    view: {
        content: [{
            tag: 'p',
            content: [{
                tag: 'label',
                content: 'id:'
            }, {
                tag: 'span',
                content: '{#link.model.id}'
            }]
        },{
            tag: 'h2',
            content: [{
                tag: 'label',
                content: 'Cost:'
            }, {
                tag: 'span',
                content: '{#link.model.cost}'
            }]
        }, {
            tag: 'h3',
            content: [{
                tag: 'label',
                content: 'network:'
            }, {
                tag: 'span',
                content: '{#link.model.net_sm_link}'
            }]
        }, {
            tag: 'p',
            content: [{
                tag: 'label',
                content: 'Source:'
            }, {
                tag: 'span',
                content: '{#link.sourceNodeID}'
            }]
        }, {
            tag: 'p',
            content: [{
                tag: 'label',
                content: 'Destination:'
            }, {
                tag: 'span',
                content: '{#link.targetNodeID}'
            }]
        }]
    }
});

nx.define('MyExtendLink', nx.graphic.Topology.Link, {
    properties: {
        sourcelabel: null,
        targetlabel: null
    },
    view: function(view) {
        view.content.push({
            name: 'source',
            type: 'nx.graphic.Text',
            props: {
                'class': 'sourcelabel',
                'alignment-baseline': 'text-after-edge',
                'text-anchor': 'start'
            }
        }, {
            name: 'target',
            type: 'nx.graphic.Text',
            props: {
                'class': 'targetlabel',
                'alignment-baseline': 'text-after-edge',
                'text-anchor': 'end'
            }
        });

        return view;
    },
    methods: {
        update: function() {

            this.inherited();

            var el, point;

            var line = this.line();
            var angle = line.angle();
            var stageScale = this.stageScale();

            // pad line
            line = line.pad(18 * stageScale, 18 * stageScale);

            if (this.sourcelabel()) {
                el = this.view('source');
                point = line.start;
                el.set('x', point.x);
                el.set('y', point.y);
                el.set('text', this.sourcelabel());
                el.set('transform', 'rotate(' + angle + ' ' + point.x + ',' + point.y + ')');
                el.setStyle('font-size', 12 * stageScale);
            }


            if (this.targetlabel()) {
                el = this.view('target');
                point = line.end;
                el.set('x', point.x);
                el.set('y', point.y);
                el.set('text', this.targetlabel());
                el.set('transform', 'rotate(' + angle + ' ' + point.x + ',' + point.y + ')');
                el.setStyle('font-size', 12 * stageScale);
            }
        }
    }
});

nx.define('MyDefaultScene', nx.graphic.Topology.DefaultScene, {

      methods: {

        dragNodeEnd: function(sender, node) {
            this.inherited(sender, node);
            console.log("new node position");
            node.x( node.x() );
            node.y( node.y() );
            console.log(node.x());
            console.log(node.y());

        },
        enterNode: function(sender, node) {
            this.inherited(sender, node);
            node.color('#f00');
        },
        leaveNode: function(sender, node) {
            this.inherited(sender, node);
            node.color(null);
        },
        enterLink: function(sender, link) {
            this.inherited(sender, link);
            link.color('#f00');
        },
        leaveLink: function(sender, link) {
            this.inherited(sender, link);
            link.color(null);
        }
    }
});

var x;

nx.define('DrawTopology', nx.ui.Component, {
    properties: {

    },
    view: {
        content: [

        {
          name: 'topology',
          type: 'nx.graphic.Topology',
          props: {
              // node config
              nodeConfig: {
                  // label display name from of node's model, could change to 'model.id' to show id
                  id: 'model.id',
                  label: 'model.name',
                  iconType: 'model.icon',
                  x: 'model.x',
                  y: 'model.y'
              },
              // link config
              linkConfig: {
                  // multiple link type is curve, could change to 'parallel' to use parallel link
                  id: 'model.id',
                  linkType: 'curve',
                  visible: 'model.visible',
                  color: 'model.color',
                  width: 'model.width',
                  sourcelabel: 'model.cost',
              },
              nodeSetConfig: {
                label: 'model.name',
                iconType: 'model.iconType',
                color: 'model.color',
                collapsed: 'model.collapsed'
              },
              tooltipManagerConfig: {
                  linkTooltipContentClass: 'MyLinkTooltip',
                  nodeTooltipContentClass: 'MyNodeTooltip'
              },
              linkInstanceClass: 'MyExtendLink',
              // canvas size
              width: 1400,
              height: 650,
              // width 100% if true
			  adaptive: true,
              // "engine" that process topology prior to rendering
              dataProcessor: 'force',
              // property name to identify unique nodes
              identityKey: 'id',
              // show icons' nodes, otherwise display dots
              showIcon: false,
              // moves the labels in order to avoid overlay
              enableSmartLabel: false,
              // smooth scaling. may slow down, if true
              enableGradualScaling: true,
              // if true, two nodes can have more than one link
              supportMultipleLink: false,
              // attach python-generated topology
              data: topologyData
              // nodeInstanceClass: 'MyExtendNode'
          },
          events: {
              'topologyGenerated': '{#_main}'
          }
        }]
    },
    methods: {
        _main: function(sender, events) {
            var topo = sender;
            topo.registerScene("myscene", "MyDefaultScene");
            topo.activateScene("myscene");
        }
    }
});

var topology = new DrawTopology();

var app = new nx.ui.Application();
// bind the topology object to the app
topology.attach( app );

// app must run inside a specific container. In our case this is the one with id="topology-container"
app.container( document.getElementById("topology-container") );
