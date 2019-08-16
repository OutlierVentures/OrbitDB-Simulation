import copy

from bloom_clock.bloom_clock import BloomClock
from bloom_clock.bloom_clock_operations import *
from crdt.gset import GSet
from network_simulator.clock import LamportClock

temp = 0

class Message(object):
    base_size = 1
    def __init__(self,sender,receiver,sending_time,data=None):
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.generated = sending_time
        self.time_sent = sending_time
        self.receive_times = {}
        self.latencies = {}
        self.clock = None
        self.id = None
        global temp
        self.temp = temp
        temp += 1
        self.type = None
        self.log = None
        self.clock_changed = False
        
    @property
    def size(self):
        return self.base_size + len(repr(self.data))

    def __repr__(self):
        return "message from " + self.sender.name + " sent to " + str(len(self.receiver)) + " nodes, generated at " + str(self.generated) + "sent at " + str(self.time_sent) + " : " + str(self.temp)

    def set_latency(self,delay,nodeID,is_managed=False):
        self.latencies[nodeID] = delay
        if is_managed:
            self.receive_times[nodeID] = self.time_sent + self.latencies[nodeID]

    def readjust(self,timestamp):
        self.time_sent = timestamp
        receivers = self.get_receivers()
        for r in receivers:
            self.receive_times[r.name] = self.time_sent + self.latencies[r.name]

    def get_receivers(self):
        receivers = []
        receiver_keys = list(self.receiver.keys())
        for r in receiver_keys:
            receivers.append(self.receiver[r])
        return receivers

    # def add_clock(self,clock,bloom=None):
    #     self.clock = clock
    #     self.id = self.clock.id

    def set_clock(self,clock):
        if self.clock_changed:
            print("no")
            exit(0)
        else:
            self.clock = clock
            self.id = self.sender.id
            self.type = clock.type
            self.clock_changed = True

    def add_log(self,log):
        self.log = GSet()
        self.log = self.log.generate_log(log)

    def get_log(self):
        return self.log

    # def __eq__(self,other):
    #     return True if self.clock.time == other.clock.time and self.clock.id == other.clock.id else False

    def __lt__(self,other):

        if self.type is "bloom":
            assert isinstance(self.clock,BloomClock)
            assert isinstance(other.clock,BloomClock)
            assert self.clock is not other.clock

            # print("printing message ids: ",self.id,other.id)

            if self.clock.happened_before(other.clock)[0] != 1:
                # print("bloom filter returns true")
                # print(self.sender.id, " before ",other.sender.id)
                print(self.clock.happened_before(other.clock)[0])
                return True

            elif self.clock.happened_after(other.clock)[0] != 1:
                # print("bloom filter returns false")
                # print(self.clock.happened_before(other.clock)[0])
                return False

            else:
                # print("bloom filter returns order based on id")
                # print("id: ", self.id,other.id)
                return True if self.id < other.id else False

        else:
            assert isinstance(self.clock,LamportClock)
            assert isinstance(other.clock,LamportClock)
            dist = self.clock.time - other.clock.time

            # if dist < 0:
            #     # print("lamport returning true")

            # print("trying to print some id's: ", self.id,other.id)

            if dist == 0 and self.id != other.id:
                print("id: ", self.id, other.id)
                return True if self.id < other.id else False

            print(self.sender.name," ---- ",other.sender.name)
            print(self.id," ---- ",other.id)
            print(self.temp, " ---- ", other.temp)
            print(dist)
            return True if dist < 0 else False

    # def __ne__(self, other):
    #     if self.type is "bloom":
    #         assert isinstance(self.clock, BloomClock)
    #         assert isinstance(other.clock, BloomClock)
    #         assert self.clock is not other.clock
    # 
    #         # print("printing message ids: ",self.id,other.id)
    # 
    #         if self.clock.happened_before(other.clock)[0] != 1:
    #             # print("bloom filter returns true")
    #             # print(self.sender.id, " before ",other.sender.id)
    #             return True
    # 
    #         elif self.clock.happened_after(other.clock)[0] != 1:
    #             # print("bloom filter returns false")
    #             return True
    # 
    #         else:
    #             # print("bloom filter returns order based on id")
    #             # print("id: ", self.id,other.id)
    #             return True if self.id != other.id else False
    # 
    #     else:
    #         assert isinstance(self.clock, LamportClock)
    #         assert isinstance(other.clock, LamportClock)
    #         dist = self.clock.time - other.clock.time
    # 
    #         if dist < 0:
    #             pass
    #             # print("lamport returning true")
    # 
    #         # print("trying to print some id's: ", self.id,other.id)
    # 
    #         if dist is 0 and self.id != other.id:
    #             return True
    # 
    #         return True if dist != 0 else False

    # def __gt__(self, other):
    # return other<self
    # def __ge__(self, other):
    # return not self<other
    # def __le__(self, other):
    # return not other<self