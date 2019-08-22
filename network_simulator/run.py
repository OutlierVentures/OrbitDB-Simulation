import copy
import itertools
import multiprocessing
import os
from uuid import uuid4

import numpy as np
import pickle
from network_simulator.peer import Peer
from network_simulator.simulation_analyser import SimulationAnalyser
from network_simulator.simulation_manager import SimulationManager

def managed_peer(name, limit):
    p = Peer(name, limit)
    return p

def create_peers(num, env):
    peers = []
    for i in range(num):
        p = managed_peer('P%d' % i, env)
        peers.append(p)
    return peers

def save_state(simulation,string):
    fileHandler = open(string, "wb")
    # print(type(simulation))
    pickle.dump(simulation, fileHandler)

def normalise_data(arrays):
    _max, _min = 0, 1000
    for a in arrays:
        temp_max = max(a)
        temp_min = min(a)
        if temp_max > _max:
            _max = temp_max
        if temp_min < _min:
            _min = temp_min

    new_list = []
    for a in arrays:
        temp = min_max_normalise(a, _min, _max)
        new_list.append(temp)
    return new_list

def min_max_normalise(x, _min, _max):
    return (x - _min) / (_max - _min)

def get_state(simulation=None,string=""):
    name = str(string)
    if simulation is not None:
        save_state(simulation,name)
    fileHandler = open(name, "rb")
    return pickle.load(fileHandler)


def run_loop(it, x_list,x_list_bloom,x_list_hybrid_bloom,x_list_dag_height,limit,parameters):

    BLOOM, HYBRID, HEIGHT = 0,1,2

    stats = SimulationAnalyser()
    bloom_stats = SimulationAnalyser()
    hybrid_bloom_stats = SimulationAnalyser()
    dag_stats = SimulationAnalyser()

    peers = []
    peers.append(managed_peer('PeerServer_one', limit))
    peers.append(managed_peer('PeerServer_two', limit))

    it -= 2
    spokes = create_peers(it, limit)

    env = SimulationManager(peers, spokes, stats,time_limit=limit, broadcast=True,
                            dropout=parameters[0], dropout_distr = parameters[1],latency=parameters[2],
                            event_type=parameters[3],message_loss=parameters[4])

    env.setup()
    a = str(it) + str(uuid4())
    states = []
    for i in range(3):
        states.append(get_state(env,string=a))

    states[BLOOM].change_clock("bloom", bloom_stats)
    states[HYBRID].change_clock("hybrid-bloom",hybrid_bloom_stats)
    states[HEIGHT].change_clock("dag-height", dag_stats)

    env.run_simulation()
    nodes = env.G.nodes()
    other_nodes = []
    for s in states:
        s.run_simulation()
        other_nodes.append(s.G.nodes())

    perc = analyse_log(nodes)
    percs = []
    for n in other_nodes:
        percs.append(analyse_log(n))

    x_list.append((it + 2,perc))
    x_list_bloom.append((it + 2,percs[BLOOM]))
    x_list_hybrid_bloom.append((it+2,percs[HYBRID]))
    x_list_dag_height.append((it+2,percs[HEIGHT]))

    os.remove(a)

def analyse_log(nodes):
    correct=incorrect=total = 0
    array = []
    for n in nodes:
        # print("printing in here")
        array.append(n.operations._payload)
        # print("opset for ", n.name)
        # print(n.operations._payload)
        # print(len(n.operations.get_payload()))
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


def simulation_paramters():
    dropout_rate = [0, 30, 70, 90]
    dropout_distr = ["normal", "skewed"]
    latency = ["consistent", "random"]
    event_creation = ["random", "skewed"]
    lost_messages = [True, False]
    hash_count = [2, 3, 5]
    filter_size = [5, 50, 100, 1000]
    permutation_one = [dropout_rate, dropout_distr, latency, event_creation, lost_messages]

    first = list(itertools.product(*permutation_one))
    first = [list(elem) for elem in first]
    # print(first)

    permutation_two = [first, hash_count, filter_size]
    second = list(itertools.product(*permutation_two))
    second = [list(elem) for elem in second]

    new = []
    for sec in second:
        temp = []
        for s in sec[0]:
            temp.append(s)
        for i in range(1, len(sec)):
            temp.append(sec[i])

        new.append(temp)

    return new

def extract_data(array):
    array = list(array)
    array = sorted(array, key=lambda array: array[0])
    array = list(zip(*array))
    x = np.array(array[0])
    y = np.array(array[1])
    return (x, y)

if __name__ == '__main__':

    limit = 10

    import matplotlib.pyplot as plt

    # parameters = simulation_paramters()
    iterations = 3
    parameters = [[60, 'skewed', 'random', 'skewed', False, 2, 500]]
    for pa in parameters:
        count = 0
        first = True
        total_x_data = None
        total_y_data = None
        st_dev_data = []
        for i in range(iterations):
            with multiprocessing.Manager() as manager:
                x_list = manager.list()
                x_list_bloom = manager.list()
                x_list_hybrid_bloom = manager.list()
                x_list_dag_height = manager.list()

                # x = [60, 'skewed', 'random', 'skewed', False, 2, 500]

                processes = []
                i = 8
                while i <= 128:
                    p = multiprocessing.Process(target=run_loop,args=(i,x_list,x_list_bloom,x_list_hybrid_bloom,
                                                                      x_list_dag_height,limit,pa))
                    processes.append(p)
                    p.start()
                    i *= 2

                for process in processes:
                    process.join()

                data = extract_data(x_list)
                x_lamport,y_lamport = data[0],data[1]
                data = extract_data(x_list_bloom)
                x_bloom,y_bloom \
                    = data[0],data[1]
                data = extract_data(x_list_hybrid_bloom)
                x_hybrid_bloom,y_hybrid_bloom = data[0],data[1]
                data = extract_data(x_list_dag_height)
                x_dag_height,y_dag_height = data[0],data[1]

                x_data = np.array([x_lamport,x_bloom,x_hybrid_bloom,x_dag_height])
                # y_data = normalise_data([y_lamport,y_bloom,y_hybrid_bloom,y_dag_height])
                y_data = np.array([y_lamport,y_bloom,y_hybrid_bloom,y_dag_height])

                y_ = [y_lamport,y_bloom,y_hybrid_bloom,y_dag_height]
                st_dev_data.append(copy.copy(y_))

                if first:
                    total_x_data = x_data
                    total_y_data = y_data
                    first = False
                else:
                    total_x_data += x_data
                    total_y_data += y_data
            count += 1

        x_data = total_x_data/count
        y_data = total_y_data/count
        x = np.std(st_dev_data, dtype=np.float64,axis=0)

        plt.plot(x_data[0],y_data[0],'xr-',label='Lamport Clock')
        plt.plot(x_data[1],y_data[1],'xb-',label='Bloom Clock')
        plt.plot(x_data[2],y_data[2],'xg-',label='Hybrid-Bloom Clock')
        plt.plot(x_data[3], y_data[3], 'xy-', label='DAG-Height Clock')
        plt.axis([0,130,70,100])
        plt.xlabel("Node Count")
        plt.ylabel("% Correct Classifications")
        plt.legend()
        name = str(pa[0]) + "~" + str(pa[1]) + "~" + str(pa[2]) + "~" + str(pa[3]) + "~" + str(pa[3]) + "~" + str(pa[4]) + "~" + str(pa[5]) + "~" + str(pa[6])
        os.mkdir("plots/" + name)
        plt.savefig("plots/" + name + "/all_together")
        plt.clf()

        fig, axs = plt.subplots(2, 2,sharey='all')
        axs[0, 0].errorbar(x_data[0],y_data[0],yerr=np.array(x[0]),ecolor='r',fmt='rs--',linewidth=1,elinewidth=2,capsize=3)
        axs[0, 0].set_title('Lamport Clock')
        axs[0, 1].errorbar(x_data[1],y_data[1],yerr=x[1],ecolor='b',fmt='bs--',linewidth=1,elinewidth=2,capsize=3)
        axs[0, 1].set_title('Bloom Clock')
        axs[1, 0].errorbar(x_data[2],y_data[2],yerr=x[2],ecolor='g',fmt='gs--',linewidth=1,elinewidth=2,capsize=3)
        axs[1, 0].set_title('Hybrid-Bloom Clock')
        axs[1, 1].errorbar(x_data[3],y_data[3],yerr=x[3],ecolor='y',fmt='ys--',linewidth=1,elinewidth=2,capsize=3)
        axs[1, 1].set_title('DAG-Height Clock')

        for ax in axs.flat:
            ax.set(xlabel='Node Count', ylabel='Successful Classifications')
        fig.tight_layout()
        fig.savefig("plots/" +name+ "/errors")

