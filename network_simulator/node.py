import copy
import random
import queue

from bloom_clock.bloom_clock import BloomClock
from network_simulator.clock import LamportClock
from crdt.gset import GSet
import operator

from network_simulator.conflict import Conflict
from network_simulator.message import Message

from bloom_clock.bloom_clock_operations import *


class Node(object):

    def __init__(self, id, length):

        self.id = id
        self.messages = [[] for i in range(length * 50)]
        self.bloom_messages = [[] for i in range(length * 50)]
        self.up = random.randint(1, 10)
        self.down = random.randint(1, self.up)
        self.is_dropped = False
        self.reactivation_time = -1
        self.incrementer = None
        self.message_queue = queue.Queue()
        self.bloom_message_queue = queue.Queue()
        self.pending_messages = queue.Queue()
        self.bloom_pending_messages = queue.Queue()
        self.stats = None
        self.bloom_stats = None

        self.clock = LamportClock()
        self.bloom_clock = BloomClock(length,3)
        self.operations = GSet()

        # env.process(self.run())

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    def receive_clock_broadcast(self, time):
        self.get_message(time)

    def get_message(self, time):
        if self.is_dropped:
            if len(self.messages[time]) > 0:
                ops = []
                for m in self.messages[time]:
                    # print("*********** " + str(m) + " ****************")
                    ops.append(m)
                ops = sorted(ops)
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
        self.is_dropped = True
        self.reactivation_time = disruption.end_time

    def reactivate(self,timestamp):
        self.is_dropped = False
        self.handle_message_backlog(timestamp)

    def send(self,msg):
        if self.is_dropped:
            # print("putting this message into the pending queue: " + str(msg))
            self.pending_messages.put(msg)
            self.bloom_pending_messages.put(msg)
        else:
            self.clock.increment()
            msg.clock = self.clock
            self.bloom_clock.send_event(id(msg))
            msg.bloom_clock = self.bloom_clock.get_clock()
            msg.receiver.receive(msg)
            self.add_to_opset(msg)

    def receive(self, msg):
        # print "RECEIVING TO BE CONSUMED AT:  " + str(msg.time_sent) + " + " + str(delay)
        self.add_to_messages(msg, msg.receive_time)

    def add_to_messages(self, msg, index):
        # print index
        # print self.id + " adding message from " + msg.sender.id
        self.messages[index].append(msg)

    def add_to_message_queue(self, msg):
        self.message_queue.put(msg)

    def handle_message(self, msg, time):
        self.add_to_opset(msg)
        i = self.messages[time].index(msg)
        self.messages[time][i] = None
        self.incrementer()
        self.clock.increment()
        self.bloom_clock = self.bloom_clock.receive_event(msg.bloom_clock)
        self.clock = self.clock.merge(msg.sender.clock)
        print(self.id + " receiving message from " + msg.sender.id)


    def handle_message_backlog(self,timestamp):
        # print(list(self.message_queue.queue))
        for m in list(self.message_queue.queue):
            msg = self.message_queue.get()
            self.bloom_clock = self.bloom_clock.receive_event(msg.bloom_clock)
            self.incrementer()
            self.clock.increment()
            self.clock = self.clock.merge(m.sender.clock)

        for m in list(self.pending_messages.queue):
            # print("======>")
            # print(m)
            m.readjust(timestamp)
            # print("readjusting ===>")
            # print(m)
            self.pending_messages.get()
            self.send(m)

    def conflict_resolution(self,time):
        print("resolving conflicts....")
        ops = []
        c = []
        for m in self.messages[time]:
            c.append(m)
            ops.append(m)

        bloom_ops = []
        for m in c:
            for n in c:
                if n is m:
                    continue
                if n.bloom_clock.get_filter() == m.bloom_clock.get_filter():
                    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$SOMETHING REALLY BAD")
            print(m)
            temp = copy.copy(m)
            temp.type = "bloom"
            print("printing a clock.....",temp.sender.id)
            print(temp.bloom_clock.get_filter())
            bloom_ops.append(temp)

        ops = sorted(ops)
        bloom_ops = sorted(bloom_ops)

        # confl = Conflict(ops)
        bloom_confl = Conflict(bloom_ops,"bloom")
        # self.stats.record_conflict(confl)
        self.bloom_stats.record_conflict(bloom_confl)

        for o in ops:
            self.add_to_opset(o)
            self.handle_message(o,time)


        # print(ops)
        print("~~~~~~~~~~~~")
        print(bloom_ops)
        # for l in self.operations.get_payload():
        #     print(l)

    def add_to_opset(self,op):
        self.operations.add(op)

# if __name__ == '__main__':
#     class Raj:
#         def __init__(self, a, b):
#             self.a = a
#             self.b = b
#
#
#     bolter = Raj(2, 1)
#     import copy
#
#     harry = copy.copy(bolter)
#     harry.a = 1
#     print(bolter.a)
#
#
#     class a:
#         def __init(self,type):
#             self.type =
#             pass]



