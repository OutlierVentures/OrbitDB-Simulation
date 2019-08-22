import multiprocessing
import random
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

def run_loop(it, x_list,x_list_bloom,x_list_hybrid_bloom,x_list_dag_height,limit,parameters):
    stats = SimulationAnalyser()
    bloom_stats = SimulationAnalyser()
    hybrid_bloom_stats = SimulationAnalyser()
    dag_stats = SimulationAnalyser()

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
    final_copy = get_state(env,string=a)

    env.run_simulation()

    copy.change_clock("bloom", bloom_stats)
    copy.run_simulation()

    other_copy.change_clock("hybrid-bloom",hybrid_bloom_stats)
    other_copy.run_simulation()

    final_copy.change_clock("dag-height", dag_stats)
    final_copy.run_simulation()

    nodes = env.G.nodes()
    _nodes = copy.G.nodes()
    __nodes = other_copy.G.nodes()
    ___nodes = final_copy.G.nodes()

    n = random.choice(list(env.G.nodes()))
    g = n.dag
    g.draw_graph("test.png")

    print("analysing normal")
    perc = analyse_log(nodes)
    print("analysing new")
    _perc = analyse_log(_nodes)
    __perc = analyse_log(__nodes)
    ___perc = analyse_log(___nodes)

    x_list.append((it + 2,perc))
    x_list_bloom.append((it + 2,_perc))
    x_list_hybrid_bloom.append((it+2,__perc))
    x_list_dag_height.append((it+2,___perc))

def analyse_log(nodes):
    correct=incorrect=total = 0
    array = []
    for n in nodes:
        print("printing in here")
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

    limit = 500

    import matplotlib.pyplot as plt

    with multiprocessing.Manager() as manager:
        x_list = manager.list()
        x_list_bloom = manager.list()
        x_list_hybrid_bloom = manager.list()
        x_list_dag_height = manager.list()

        starttime = time.time()
        processes = []

        it = 100

        x = [60, 'skewed', 'random', 'skewed',False,2,500]

        for i in range(49,250,75):
            p = multiprocessing.Process(target=run_loop,args=(i,x_list,x_list_bloom,x_list_hybrid_bloom,x_list_dag_height,limit,x))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()

        def extract_data(array):
            array = list(array)
            array = sorted(array,key=lambda array: array[0])
            array = list(zip(*array))
            x = np.array(array[0])
            y = np.array(array[1])
            return (x,y)

        data = extract_data(x_list)
        x_lamport,y_lamport = data[0],data[1]
        data = extract_data(x_list_bloom)
        x_bloom,y_bloom = data[0],data[1]
        data = extract_data(x_list_hybrid_bloom)
        x_hybrid_bloom,y_hybrid_bloom = data[0],data[1]
        data = extract_data(x_list_dag_height)
        x_dag_height,y_dag_height = data[0],data[1]


        plt.plot(x_list_,y_list_,'xr-',label='Lamport Clock')
        plt.plot(x_list_bloom_,y_list_bloom_,'xb-',label='Bloom Clock')
        plt.plot(x_list_hybrid_bloom_,y_list_hybrid_bloom_,'xg-',label='Hybrid-Bloom Clock')
        plt.plot(x_list_dag_height_, y_list_dag_height_, 'xy-', label='DAG-Height Clock')

        plt.axis([45,180,0, 100])
        plt.xlabel("Node Count")
        plt.ylabel("% Correct Classifications")
        plt.legend()
        plt.show()

