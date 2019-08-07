from bloom_clock.bloom_clock_operations import *

temp = 0

class Message(object):
    base_size = 1
    def __init__(self,sender,receiver,sending_time,data=None):
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.generated = sending_time
        self.time_sent = sending_time
        self.receive_time = -1
        self.latency = -1
        self.clock = None
        self.id = None
        global temp
        self.temp = temp
        temp += 1

        self.type = None
        
    @property
    def size(self):
        return self.base_size + len(repr(self.data))

    def __repr__(self):
        return "message from " + self.sender.id + " sent to " + self.receiver.id + " generated at " + str(self.generated) + "sent at " + str(self.time_sent) + " with latency " + str(self.latency) + " : " + str(self.temp)

    def set_latency(self,delay,is_managed=False):
        self.latency = delay

        if is_managed:
            self.receive_time = self.time_sent + self.latency

    def readjust(self,timestamp):
        self.time_sent = timestamp
        self.receive_time = self.time_sent + self.latency

    def add_clock(self,clock,bloom=None):
        self.clock = clock
        self.bloom_clock = bloom
        self.id = (self.clock.time,self.sender.id)

    # def __eq__(self,other):
    #     return True if self.clock.time == other.clock.time and self.clock.id == other.clock.id else False

    def __lt__(self,other):

        if self.type is "bloom":
            if self.bloom_clock.happened_before(other.bloom_clock)[0] != 1:
                print("bloom filter returns true")
                print(self.sender.id, " before ",other.sender.id)
                return True

            elif self.bloom_clock.happened_after(other.bloom_clock)[0] != 1:
                print("bloom filter returns false")
                return False

            else:
                print("bloom filter returns order based on id")
                return True if self.clock.id < other.clock.id else False

        else:
            dist = self.clock.time - other.clock.time

            if dist < 0:
                print("lamport returning true")

            if dist is 0 and self.id is not other.clock.id:
                    return True if self.clock.id < other.clock.id else False

            return True if dist < 0  else False

    # def __deepcopy__(self, memodict={}):
    #     cpyobj = type(self)()  # shallow copy of whole object
    #     cpyobj.deep_cp_attr = copy.deepcopy(self.other_attr, memodict)  # deepcopy required attr
    #
    #     return cpyobj