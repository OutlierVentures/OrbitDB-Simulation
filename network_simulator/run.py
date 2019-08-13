# import random
# import simpy
# # from node import Node
# from nodemanager import NodeManager
# from nodemanager import PingHandler
# from nodemanager import PeerRequestHandler
# from networkx.drawing.nx_agraph import graphviz_layout

# NODE_COUNT = 3
# DURATION = 5
# KB = 1024/8
# #VISUALIZATION = True
# VISUALIZATION = False
#
# def managed_peer(name, env):
#     p = Node(name, env)
#     p.properties.append(NodeManager(p))
#     p.properties.append(PeerRequestHandler())
#     p.properties.append(PingHandler())
#
#     return p
#
# def create_peers(peerserver, num):
#     peers = []
#     for i in range(num):
#         p = managed_peer('P%d' % i, env)
#
#         connection_manager = p.properties[0]
#         x = random.randint(0,2)
#         #x = 0
#         print "connecting to server"
#         connection_manager.connect_peer(peerserver[x])
#         peers.append(p)
#         #p.connect(peerserver[x])
#     #
#     # for p in peers[:int(num * 0.5)]:
#     #     p.up = max(384, random.gauss(12000, 6000)) * KB
#     #     p.down = max(128, random.gauss(4800, 2400)) * KB
#     #
#     # for p in peers[int(num * 0.5):]:
#     #     p.up = p.down = max(10000, random.gauss(100000, 50000)) * KB
#
#     return peers
#
# env = simpy.Environment()
#
# """hub and spoke network model"""
# peers = []
# peers.append(managed_peer('PeerServer_one', env))
# peers.append(managed_peer('PeerServer_two', env))
# peers.append(managed_peer('PeerServer_three', env))
#
# for p in peers:
#     for l in peers:
#         if l is p:
#             continue
#         else:
#             p.connect(l)
#
# peers += create_peers(peers, NODE_COUNT)
#
# print 'starting sim'
# if VISUALIZATION:
#     from visualize import Visualizer
#     Visualizer(env, peers)
# else:
#     env.run(until=DURATION)
import numpy as np
import pickle

from network_simulator.node import Node
from network_simulator.simulation_analyser import SimulationAnalyser
from network_simulator.simulation_manager import SimulationManager


def managed_peer(name, limit):
    p = Node(name, limit)
    # p.properties.append(p)
    # p.properties.append(PeerRequestHandler())
    # p.properties.append(PingHandler())

    return p

def create_peers(num, env):
    peers = []
    for i in range(num):
        p = managed_peer('P%d' % i, env)
        peers.append(p)
    return peers

def save_state(simulation):
    fileHandler = open("network", "wb")
    print(type(simulation))
    pickle.dump(simulation, fileHandler)

def get_state(simulation=None):
    if simulation is not None:
        save_state(simulation)
    fileHandler = open("network", "rb")
    return pickle.load(fileHandler)


if __name__ == '__main__':

    limit = 2000

    import matplotlib.pyplot as plt

    x_list = []
    y_list = []
    x_list_bloom = []
    y_list_bloom = []

    for i in range(1,18):

        stats = SimulationAnalyser()
        bloom_stats = SimulationAnalyser()

        peers = []
        peers.append(managed_peer('PeerServer_one', limit))
        peers.append(managed_peer('PeerServer_two', limit))
        # peers.append(managed_peer('PeerServer_three', limit))

        spokes = create_peers(i,limit)

        env = SimulationManager(peers,spokes,stats,bloom_stats,time_limit=limit,broadcast=True)
        env.setup()
        copy = get_state(env)
        env.run_simulation()

        copy.change_clock("bloom",bloom_stats)
        copy.run_simulation()

        x_list.append(i+2)
        x_list_bloom.append(i+2)
        y_list.append(int(stats.percent_correct))
        y_list_bloom.append(int(bloom_stats.percent_correct))
        stats.get_results()
        bloom_stats.get_results()

    print("****************")
    print(x_list,y_list)
    print(x_list_bloom,y_list_bloom)

    x_list = np.array(x_list)
    y_list = np.array(y_list)
    x_list_bloom = np.array(x_list_bloom)
    y_list_bloom = np.array(y_list_bloom)
    plt.plot(x_list, y_list, 'xr-')
    plt.plot(x_list_bloom,y_list_bloom,'xb-')
    plt.axis([3, 20, 0, 100])
    plt.xlabel("Node Count")
    plt.ylabel("% Correct Classifications")
    plt.show()

