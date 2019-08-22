import networkx as nx
import matplotlib.pyplot as plt
import numpy
import numpy as np
import random
import progressbar
from time import sleep
from network_simulator.message import Message
from network_simulator.disruption import Disruption
from network_simulator.simulation_analyser import SimulationAnalyser


class SimulationManager:

    def __init__(self,hubs,spokes,analyser,size=None,time_limit=None,broadcast=False,dropout=30,
                 dropout_distr="normal",latency="random",event_type="random",message_loss=True,hash_count=3,filter_size=50):

        self.hubs = hubs
        self.spokes = spokes
        self.G = nx.DiGraph()
        self._activeNodes = set()
        self._droppedNodes = set()

        self.size = size
        self.timeLimit = time_limit
        self.dropProb = dropout
        self.dropDistr = dropout_distr

        if latency == "consistent":
            for h in self.hubs:
                h.up,h.down = 5,1
            for s in self.spokes:
                s.up,s.down = 5,1
        #
        if message_loss:
            for h in self.hubs:
                h.change_message_protocol()
            for s in self.spokes:
                s.change_message_protocol()
        #
        hash_count,filter_size = 3,500
        for h in self.hubs:
            h.set_bloom_parameters(hash_count,filter_size)
        for s in self.spokes:
            s.set_bloom_parameters(hash_count,filter_size)

        self.event_creation = event_type

        self.current_time = 0
        self.messages = []
        self._messagesGenerated = 0
        self._messageCount = 0
        self.stats = analyser

        self.broadcast = broadcast

        self.disruptions = []
        self.incrementer = self.new_message

#        self.messages = [[]]*self.time_limit

    def new_message(self):
        self._messageCount += 1

    def add_nodes(self,nodes):
        for n in nodes:
            self.G.add_node(n)

    def setup(self):
        #add hubs and spokes to graph
        print("adding nodes...")
        self.add_nodes(self.hubs)
        self.add_nodes(self.spokes)
        self.stat_generator()
        print("connecting network...")
        self.connect_hubs()
        self.connect_spokes()
        self._messagesGenerated = self.create_dropout_list()
        self._activeNodes = set(self.G.nodes())

    def get_graph(self):
        return self.G

    def stat_generator(self):
        for n in self.G.nodes():
            n.stats = self.stats

    def get_incrementer(self):
        return self.incrementer

    def time(self):
        return self.current_time

    def tick(self):
        self.current_time += 1

    def run_simulation(self):
        if self.current_time is not 0:
            print("Simulation can only be run from the beginning! ")
            return

        print("beginning simulation...")
        #for i in range(self.current_time,self.time_limit * 20):

        while self._messageCount < self._messagesGenerated:
            # print("running Simulation iteration %d" % self.current_time)

            self.reactivate_nodes()
            self.send_message(self.get_next_message())
            self.receive_messages()
            self.drop_nodes()
            self.tick()
            #self.draw_network()

        # print(str(self._messageCount) + " = " + str(self._messagesGenerated))

        # for n in self.G.nodes():
        #     print "-----"
        #     print n.id
        #     print n.messages

# Helper functions

    def reactivate_nodes(self):
        temp = set()
        for n in self._droppedNodes:
            if self.current_time == n.reactivation_time:
                # print(n.name + " reconnected")
                n.reactivate(self.current_time)
                self._activeNodes.add(n)
                temp.add(n)

        for t in temp:
            self._droppedNodes.remove(t)

    def receive_messages(self):
        self.broadcast_clock()

    def get_latency(self,n,m):
        return self.G.get_edge_data(n,m)['weight']

    def send_message(self,msg):
        if msg is None:
            pass
        else:
            for m in msg:
                sender = m.sender
                receivers = m.get_receivers()
                for r in receivers:
                    if not self.G.has_edge(sender, r):
                        # print "Creating connection between " + msg.sender.id + " and " + r.id
                        self.G.add_edge(sender, r, weight=sender.up + r.down)
                        self.G.add_edge(r, sender, weight=sender.down + r.up)

                    delay = self.get_latency(sender,r)
                    m.set_latency(delay,r.name,True)

            sender.send(m)

    def drop_nodes(self):
        if self.current_time < len(self.disruptions):
            d = self.disruptions[self.current_time]
            if d is not None:
                self.handle_disruption(d)

    def handle_disruption(self,disruption):
        assert isinstance(disruption,Disruption)
        try:
            assert disruption.start_time == self.current_time
        except AssertionError:
            print(disruption.start_time)
            print("current time = " + str(self.current_time))
            exit(0)

        assert disruption.node in self.G.nodes()

        n = disruption.node
        n.disconnect(disruption)
        self._activeNodes.remove(n)
        self._droppedNodes.add(n)

    def broadcast_clock(self):
        for n in self.G.nodes():
            n.receive_clock_broadcast(self.current_time)

    def get_next_message(self):
        if self.current_time >= len(self.messages):
            pass
        else:
            return self.messages[self.current_time]

    def create_dropout_list(self):
        bar = progressbar.ProgressBar(maxval=self.timeLimit, \
                                      widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()

        print("creating dropout list...")
        counter = 0

        current_dropouts = set()
        reconnections = [[] for i in range(self.timeLimit * 1000)]

        # print(list(self.G.nodes()))
        allNodes = numpy.array(self.G.nodes())
        np.random.shuffle(allNodes)
        bias_weights = [(x /(len(allNodes) + 1)) for x in range(1,len(allNodes)+1)]
        prob = np.array(bias_weights) / np.sum(bias_weights)


        for i in range(self.timeLimit):
            if reconnections[i]:
                for n in reconnections[i]:
                    current_dropouts.remove(n)

            nodes = list(set(self.G.nodes()) - current_dropouts)

            drop_prob = random.randint(0,100)

            if drop_prob < self.dropProb and nodes:
                reconnect_time = random.randint(i+1, i+50)

                if self.dropDistr == "skewed":
                    assert None not in current_dropouts
                    n = np.random.choice(allNodes,p=prob)
                    while n in current_dropouts:
                        n = np.random.choice(allNodes,p=prob)

                else:
                    n = random.choice(nodes)

                current_dropouts.add(n)
                index = nodes.index(n)
                del nodes[index]
                reconnections[reconnect_time].append(n)
                d = Disruption(n,i,reconnect_time)
                self.disruptions.append(d)

            else:
                self.disruptions.append(None)

            # if self.event_creation == "skewed":
            #     network = np.array(self.G.nodes())
            #     np.random.shuffle(network)
            #     bias_weights = [(x / (len(network) + 1)) for x in range(1, len(network) + 1)]
            #     prob = np.array(bias_weights) / np.sum(bias_weights)
            #     sender = np.random.choice(allNodes,p=prob)
            #
            # else:
            sender = random.choice(list(self.G.nodes()))

            if self.broadcast:
                receivers = {}
                for n in list(set(self.G.nodes())):
                    if n is sender:
                        continue
                    else:
                        receivers[n.name] = n
                        counter +=1

                m = Message(sender,receivers,i)
                self.messages.append([m])

            else:
                number_of_receivers = random.randint(0, len(self.G) - 1 - len(current_dropouts))
                if number_of_receivers is 0:
                    bar.update(i + 1)
                    sleep(0.1)
                    self.messages.append(None)
                    continue
                receivers = set()
                counter += number_of_receivers

                # print "Recievers will be of count: " + str(number_of_receivers) + ": "
                messages = []
                nodes_temp = set(self.G.nodes())
                nodes_temp.remove(sender)
                active_nodes = list(nodes_temp - current_dropouts)
                while number_of_receivers > 0:
                    n = random.choice(active_nodes)
                    # print str(n.id)
                    index = active_nodes.index(n)
                    del active_nodes[index]
                    # print nodes
                    number_of_receivers -= 1
                    m = Message(sender, n, i)
                    messages.append(m)

            #self.messages.append(messages)

            bar.update(i+1)
            sleep(0.1)

        bar.finish()
        # print(self.messages)
        # print(self.disruptions)
        return counter

    def connect_hubs(self):
        for h in self.hubs:
            partner = self.find_lowest_latency_hub(h)
            self.G.add_edge(h,partner,weight=h.up+partner.down)
            self.G.add_edge(partner,h,weight=h.down+partner.up)
            h.incrementer = self.incrementer

    def find_lowest_latency_hub(self,node):
        temp = None
        for h in self.hubs:
            if h is node:
                continue
            elif temp is None:
                temp = h
            else:
                x = (node.up + temp.down,node.down+temp.up)
                l = (node.up + h.down,node.down+h.down)
                if x > l:
                    temp = h

        return temp

    def connect_spokes(self):
        for s in self.spokes:
            s.incrementer = self.incrementer
            # get the number of hubs in the network
            number_hubs = len(self.hubs)
            # draw a random number of hubs to connect a node to
            x = random.randint(1,number_hubs)
            #print x
            # make the connections between each spoke and the randomly
            # selected hubs
            for i in range(x):
                n = random.randint(0,number_hubs-1)
                selected_hub = self.hubs[n]
                spoke_to_hub_latency = s.up + selected_hub.down
                hub_to_spoke_latency = s.down + selected_hub.up
                self.G.add_edge(s,selected_hub,weight=spoke_to_hub_latency)
                self.G.add_edge(selected_hub,s,weight=hub_to_spoke_latency)

    def draw_network(self):
        pos = nx.spring_layout(self.G)
        # print(self.G.nodes())
        node_list = ['red' if not node in self.hubs else 'skyblue' for node in self.G.nodes()]

        hubs = self.hubs
        spokes = self.spokes
        #
        nx.draw_networkx_nodes(self.G,pos,ax=None,node_size=200,nodelist=hubs,node_color='b')
        nx.draw_networkx_nodes(self.G,pos,ax=None,node_size=50,nodelist=spokes,node_color='r')

        #nx.draw_networkx_edges(g, pos,arrows=False)
        labels = nx.get_edge_attributes(self.G,'weight')
        #nx.draw(self.G, node_size=500, node_color=node_list,edge_labels=True)
        nx.draw_networkx_edges(self.G,pos,ax=None,edge_color='black', arrows=True)
        #nx.draw_networkx_edge_labels(self.G,pos,edge_labels=labels, font_size =8)
        plt.axis('off')
        plt.show()

    def change_clock(self,type,stats):
        for n in self.G.nodes():
            n.change_type(type)
            n.stats = stats
