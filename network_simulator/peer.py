import random
import uuid
from collections import Iterable

from DAG.merkle_dag import DAG,Node
from bloom_clock.bloom_clock import BloomClock, HybridLamportBloom
from network_simulator.clock import LamportClock
from crdt.gset import GSet

from network_simulator.conflict import Conflict
from network_simulator.message import Message


class Peer(object):

    def __init__(self, id, length):

        self.name = id
        self.id = uuid.uuid4()
        self.messages = [[] for i in range(length * 50)]
        self.bloom_messages = [[] for i in range(length * 50)]
        self.up = random.randint(1,10)
        self.down = random.randint(1, self.up)
        self.is_dropped = False
        self.lose_messages = False
        self.reactivation_time = -1
        self.incrementer = None
        self.message_queue = []
        self.pending_messages = []
        self.stats = None
        self.bloom_stats = None

        self.filter_size = -1
        self.hash_count = -1

        self.clock = LamportClock()
        self.length = length
        self.operations = GSet()

        self.dag = DAG()

        # env.process(self.run())

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

    def change_type(self,type):
        if type == "bloom":
            self.clock = BloomClock(hash_count=self.hash_count,filter_size=self.filter_size)
        if type == 'hybrid-bloom':
            self.clock = HybridLamportBloom(hash_count=self.hash_count,filter_size=self.filter_size)
        if type == 'dag-height':
            self.clock.dag = True

    def receive_clock_broadcast(self, time):
        self.get_message(time)

    def get_message(self, time):
        if self.is_dropped:
            if len(self.messages[time]) > 0:
                ops = []
                for m in self.messages[time]:
                    # print("*********** " + str(m) + " ****************")
                    ops.append(m)
                #ops = sorted(ops)
                for o in ops:
                    self.add_to_message_queue(o)

        elif len(self.messages[time]) > 1:
            print("conflict resolution time")
            self.conflict_resolution(time)
        elif len(self.messages[time]) == 1:
            m = self.messages[time][0]
            self.handle_message(m, time)
        else:
            # print "never getting in here"
            pass

    def disconnect(self, disruption):
        assert not self.is_dropped

        self.is_dropped = True
        self.reactivation_time = disruption.end_time

    def reactivate(self,timestamp):
        assert self.is_dropped
        assert timestamp == self.reactivation_time

        self.is_dropped = False
        self.handle_message_backlog(timestamp)

    def send(self,msg):
        print(self.name," sending a message")
        self.clock.send_event(id(msg))
        msg.set_clock(self.clock.get_clock())
        print(self.name," adding to opset")
        self.add_to_opset(msg)
        if self.is_dropped:
            # print("putting this message into the pending queue: " + str(msg))
            self.pending_messages.append(msg)
        else:
            receivers = msg.get_receivers()
            for r in receivers:
                r.receive(msg)

    def receive(self, msg):
        # print "RECEIVING TO BE CONSUMED AT:  " + str(msg.time_sent) + " + " + str(delay)
        print(msg.receive_times)
        self.add_to_messages(msg, msg.receive_times[self.name])

    def add_to_messages(self, msg, index):
        # print index
        # print self.id + " adding message from " + msg.sender.id
        self.messages[index].append(msg)

    def add_to_message_queue(self, msg):
        self.message_queue.append(msg)

    def handle_message(self, msg, time,dag=True):
        i = self.messages[time].index(msg)
        self.messages[time][i] = None
        self.incrementer()
        self.clock = self.clock.receive_event(msg.clock)
        print(self.name + " receiving message from " + msg.sender.name, msg.temp)
        self.add_to_opset(msg)

    def handle_message_backlog(self,timestamp):
        self.pending_messages = sorted(self.pending_messages)
        while len(self.pending_messages):
            m = self.pending_messages.pop(0)
            receivers = m.get_receivers()
            if not self.lose_messages:
                m.readjust(timestamp)
                for r in receivers:
                    r.receive(m)
            else:
                for r in receivers:
                    r.incrementer()

        while len(self.message_queue):
            msg = self.message_queue.pop(0)
            if not self.lose_messages:
                self.add_to_opset(msg)
                self.clock = self.clock.receive_event(msg.clock)
            self.incrementer()

    def conflict_resolution(self,time):
        print("resolving conflicts....")
        c = self.messages[time]
        random.shuffle(c)
        ops = []
        for m in c:
            ops.append(m)

        ops = sorted(ops)

        if not all(o.sender.id == ops[0].sender.id for o in ops):

            if isinstance(self.clock,LamportClock):
                confl = Conflict(ops)
            if isinstance(self.clock,BloomClock):
                confl = Conflict(ops,"bloom")
            if isinstance(self.clock,HybridLamportBloom):
                confl = Conflict(ops,"hybrid-bloom")

            # self.stats.record_conflict(confl)
            self.stats.record_conflict(confl)
        else:
            print("ignore")

        for o in ops:
            self.handle_message(o,time)

    def add_to_opset(self,op):
        assert isinstance(op,Message)
        assert isinstance(op.sender.operations,GSet)

        if op.sender is not self:
            print("about to perform a merge between ",self.name,op.sender.name)
            self.operations = self.operations.merge(op.get_log())
            self.dag = self.dag.merge(op.dag)
            assert op.dag is not None
            # op.sender.operations = self.operation

        else:
            self.dag.add(Node(id(op),op))
            op.set_dag(self.dag)
            self.operations.add(op)
            op.add_log(self.operations)



    #
    # def add_to_dag(self,op):
    #     print(self.name, " in the else block")
    #     if op.sender is not self:
    #         assert op.dag is not None
    #         self.dag = self.dag.merge(op.dag)
    #     else:
    #         print(self.name, " dag added")
    #         assert self.dag is not None
    #
    #         op.set_dag(self.dag)
    #         assert op.dag is not None

    def change_message_protocol(self):
        self.lose_messages = True

    def set_bloom_parameters(self,hash_count,filter_size):
        self.hash_count = hash_count
        self.filter_size = filter_size
