import itertools

def simulation_paramters():
    node_count = [8,16,32,64,128]
    clock_type = ["lamport","dag-height"]
    bloom_clock_type = ["bloom","hybrid-bloom"]

    dropout_rate = [0,30,70,90]
    dropout_distr = ["normal","skewed"]
    latency = ["consistent","random"]
    event_creation = ["random","skewed"]
    lost_messages = [True,False]
    hash_count = [2,3,5]
    filter_size = [50,100,1000]
    permutation_one = [dropout_rate,dropout_distr,latency,event_creation,lost_messages,hash_count,filter_size,node_count]


    first = list(itertools.product(*permutation_one))
    first = [list(elem) for elem in first]

    return first

    permutation_two = [first,hash_count,filter_size]
    second = list(itertools.product(*permutation_two))
    second = [list(elem) for elem in second]

    new = []
    for sec in second:
        temp = []
        for s in sec[0]:
            temp.append(s)
        for i in range (1,len(sec)):
            temp.append(sec[i])

        new.append(temp)

    return new

if __name__ == '__main__':
    print(simulation_paramters())
    print(len(simulation_paramters()))