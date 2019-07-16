import random
import simpy
from node import Node
from nodemanager import NodeManager
from nodemanager import PingHandler
from nodemanager import PeerRequestHandler
from networkx.drawing.nx_agraph import graphviz_layout

NODE_COUNT = 50
DURATION = 5
KB = 1024/8
VISUALIZATION = True
#VISUALIZATION = False

def managed_peer(name, env):
    p = Node(name, env)
    p.properties.append(NodeManager(p))
    p.properties.append(PeerRequestHandler())
    p.properties.append(PingHandler())

    return p


def create_peers(peerserver, num):
    peers = []
    for i in range(num):
        p = managed_peer('P%d' % i, env)

        connection_manager = p.properties[0]
        x = random.randint(0,2)
        connection_manager.connect_peer(peerserver[x])
        peers.append(p)
        p.connect(peerserver[x])

    for p in peers[:int(num * 0.5)]:
        p.up = max(384, random.gauss(12000, 6000)) * KB
        p.down = max(128, random.gauss(4800, 2400)) * KB

    for p in peers[int(num * 0.5):]:
        p.up = p.down = max(10000, random.gauss(100000, 50000)) * KB

    return peers

env = simpy.Environment()

"""hub and spoke network model"""
peers = []
peers.append(managed_peer('PeerServer_one', env))
peers.append(managed_peer('PeerServer_two', env))
peers.append(managed_peer('PeerServer_three', env))

for p in peers:
    for l in peers:
        if l is p:
            continue
        else:
            p.connect(l)

peers += create_peers(peers, NODE_COUNT)

print 'starting sim'
if VISUALIZATION:
    from visualize import Visualizer
    Visualizer(env, peers)
else:
    env.run(until=DURATION)
