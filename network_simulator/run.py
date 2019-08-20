import multiprocessing
import time

import numpy as np
import pickle

from network_simulator.peer import Peer
from network_simulator.simulation_analyser import SimulationAnalyser
from network_simulator.simulation_manager import SimulationManager


def managed_peer(name, limit):
    p = Peer(name, limit)
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

def save_state(simulation,string):
    fileHandler = open(string, "wb")
    print(type(simulation))
    pickle.dump(simulation, fileHandler)

def get_state(simulation=None,string=""):
    name = str(string)
    if simulation is not None:
        save_state(simulation,name)
    fileHandler = open(name, "rb")
    return pickle.load(fileHandler)

def run_loop(it, x_list,x_list_bloom,x_list_hybrid_bloom,limit,parameters):
    stats = SimulationAnalyser()
    bloom_stats = SimulationAnalyser()
    hybrid_bloom_stats = SimulationAnalyser()

    peers = []
    peers.append(managed_peer('PeerServer_one', limit))
    peers.append(managed_peer('PeerServer_two', limit))

    it += 1
    spokes = create_peers(it, limit)

    env = SimulationManager(peers, spokes, stats, bloom_stats, time_limit=limit, broadcast=True,
                            dropout=parameters[0], dropout_distr = parameters[1],latency=parameters[2],
                            event_type=parameters[3],message_loss=parameters[4])

    env.setup()
    a = str(it)
    copy = get_state(env,string=a)
    other_copy = get_state(env, string=a)

    env.run_simulation()

    copy.change_clock("dag-height", bloom_stats)
    copy.run_simulation()

    # other_copy.change_clock("hybrid-bloom",hybrid_bloom_stats)
    # other_copy.run_simulation()

    nodes = env.G.nodes()
    _nodes = copy.G.nodes()
    # __nodes = other_copy.G.nodes()

    perc = analyse_log(nodes)
    _perc = analyse_log(_nodes)
    # __perc = analyse_log(__nodes)

    x_list.append((it + 2,perc))
    x_list_bloom.append((it + 2,_perc))
    # x_list_hybrid_bloom.append((it+2,__perc))

def analyse_log(nodes):
    correct=incorrect=total = 0
    array = []
    for n in nodes:
        array.append(n.operations._payload)
        print("opset for ", n.name)
        print(n.operations._payload)
        print(len(n.operations.get_payload()))
    for i in range(len(array[0])):
        for m in range(i + 1, len(array[0])):
            if i == m:
                continue
            if array[0][i].time_sent <= array[0][m].time_sent:
                correct += 1
            else:
                incorrect += 1
            total += 1

    perc = ((correct) / (total)) * 100
    return perc


if __name__ == '__main__':

    limit = 100

    import matplotlib.pyplot as plt

    with multiprocessing.Manager() as manager:
        x_list = manager.list()
        x_list_bloom = manager.list()
        x_list_hybrid_bloom = manager.list()

        starttime = time.time()
        processes = []

        it = 100

        x = [60, 'skewed', 'random', 'skewed',True,2,500]

        for i in range(49,500,75):
            p = multiprocessing.Process(target=run_loop,args=(i,x_list,x_list_bloom,x_list_hybrid_bloom,limit,x))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()

        x_list = list(x_list)
        x_list = sorted(x_list, key=lambda x: x[0])
        x_list_bloom = list(x_list_bloom)
        x_list_bloom = sorted(x_list_bloom, key=lambda x: x[0])
        x_list_hybrid_bloom = list(x_list_hybrid_bloom)
        x_list_hybrid_bloom = sorted(x_list_hybrid_bloom, key=lambda x: x[0])

        print(x_list)

        x_list = list(zip(*x_list))
        x_list_bloom = list(zip(*x_list_bloom))
        x_list_hybrid_bloom = list(zip(*x_list_hybrid_bloom))

        print(x_list_hybrid_bloom)

        x_list_ = np.array(x_list[0])
        y_list_ = np.array(x_list[1])

        x_list_bloom_ = np.array(x_list_bloom[0])
        y_list_bloom_ = np.array(x_list_bloom[1])

        x_list_hybrid_bloom_ = np.array(x_list_hybrid_bloom[0])
        y_list_hybrid_bloom_ = np.array(x_list_hybrid_bloom[1])

        plt.plot(x_list_,y_list_,'xr-',label='Lamport Clock')
        plt.plot(x_list_bloom_,y_list_bloom_,'xb-',label='Bloom Clock')
        plt.plot(x_list_hybrid_bloom_,y_list_hybrid_bloom_,'xg-',label='Hybrid-Bloom Clock')

        plt.axis([45,180,0, 100])
        plt.xlabel("Node Count")
        plt.ylabel("% Correct Classifications")
        plt.legend()
        plt.show()


    # spokes = create_peers(30, limit)
    # env = SimulationManager(peers, spokes, stats, bloom_stats, time_limit=limit, broadcast=True)
    # env.setup()
    # copy = get_state(env)
    # env.run_simulation()
    #
    # copy.change_clock("bloom", bloom_stats)
    # copy.run_simulation()
    #
    # nodes = copy.G.nodes()
    # _nodes = env.G.nodes()
    #
    # correct = 0
    # incorrect = 0
    # total = 0
    #
    # messages = copy.messages
    #
    # a = []
    # print("printing lamport clock opsets")
    # for n in _nodes:
    #     a.append(n.operations._payload)
    #     print("opset for ",n.name)
    #     print(n.operations._payload)
    #     print(len(n.operations.get_payload()))
    #
    #     # x = n.operations.get_payload()
    #     # for msg in x:
    #     #     for g in x:
    #     #         if x.index(g) < x.index(msg):
    #     #             continue
    #     #         if msg is g:
    #     #             continue
    #     #         else:
    #     #             if msg < g:
    #     #                 print("yes!!!")
    #     #             else:
    #     #                 if g < msg:
    #     #                     print("fine")
    #     #                 else:
    #     #                     print("circularity")
    #     #                 print("no")
    #     #                 print(msg,"**** ",g)
    #
    #
    # for i in range(len(a[0])):
    #     for m in range(i+1,len(a[0])):
    #         if i == m:
    #             continue
    #         # if i < 50 and j < 50:
    #         #     print("comparing: ", a[j][i].time_sent,a[j][m].time_sent)
    #         if a[0][i].time_sent <= a[0][m].time_sent:
    #             # print("correct")
    #             correct += 1
    #         else:
    #             # print("incorrect")
    #             incorrect += 1
    #         total += 1
    #
    # print(correct," + ",incorrect," = ",total)
    #
    # perc = ((correct)/(total))*100
    #
    # print(perc,"%")
    #
    # b = []
    # #
    # for n in nodes:
    #     b.append(n.operations._payload)
    #     print("opset for ",n.name)
    #     print(n.operations._payload)
    #
    #
    # correct = 0
    # incorrect = 0
    # total = 0
    #
    # for i in range(len(b[0])):
    #     for m in range(i,len(b[0])):
    #         if i == m:
    #             continue
    #         if b[0][i].time_sent <= b[0][m].time_sent:
    #             correct += 1
    #         else:
    #             incorrect += 1
    #         total += 1
    #
    # perc = ((correct)/(total))*100
    #
    # print(perc,"%")
    #
    # for i in range(len(a[0])):
    #     for m in range(len(a)):
    #         for j in range(len(a)):
    #             if m == j:
    #                 continue
    #             if a[j][i].temp != a[m][i].temp:
    #                 print("diff")
    #             else:
    #                 print("same")


    #
    #
    # for i in range(1,18):
    #
    #     stats = SimulationAnalyser()
    #     bloom_stats = SimulationAnalyser()
    #
    #     peers = []
    #     peers.append(managed_peer('PeerServer_one', limit))
    #     peers.append(managed_peer('PeerServer_two', limit))
    #     # peers.append(managed_peer('PeerServer_three', limit))
    #
    #     spokes = create_peers(i,limit)
    #
    #     env = SimulationManager(peers,spokes,stats,bloom_stats,time_limit=limit,broadcast=True)
    #     env.setup()
    #     copy = get_state(env)
    #     env.run_simulation()
    #
    #     copy.change_clock("bloom",bloom_stats)
    #     copy.run_simulation()
    #
    #     x_list.append(i+2)
    #     x_list_bloom.append(i+2)
    #     y_list.append(int(stats.percent_correct))
    #     y_list_bloom.append(int(bloom_stats.percent_correct))
    #     stats.get_results()
    #     bloom_stats.get_results()
    #
    # print("****************")
    # print(x_list,y_list)
    # print(x_list_bloom,y_list_bloom)
    #
    # x_list = np.array(x_list)
    # y_list = np.array(y_list)
    # x_list_bloom = np.array(x_list_bloom)
    # y_list_bloom = np.array(y_list_bloom)
    # plt.plot(x_list, y_list, 'xr-')
    # plt.plot(x_list_bloom,y_list_bloom,'xb-')
    # plt.axis([3, 20, 0, 100])
    # plt.xlabel("Node Count")
    # plt.ylabel("% Correct Classifications")
    # plt.show()

