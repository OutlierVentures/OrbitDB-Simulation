import random

from bloom_clock.bloom_filter import BloomFilter
import math
import copy

from network_simulator.clock import Clock, LamportClock


# IDList = []
# for i in range(0,1000000):
#     IDList.append(i)
#
# def key_generator():
#     global IDList
#     x = random.choice(IDList)
#     IDList.pop(IDList.index(x))
#     return x


class BloomClock(Clock):

    def __init__(self,time_iterations=None,filter=None,id=None,hash_count=3,filter_size=50):
        self.size = filter_size
        self.hash_count = hash_count
        self.filter = BloomFilter(self.size,self.hash_count)
        if filter is not None:
            if isinstance(filter,BloomFilter):
                self.set_filter(filter)
            else:
                self.filter = BloomFilter(self.size,self.hash_count)
                self.filter.bit_array = filter
        self.time_iterations = time_iterations
        self.type = "bloom"

        self.id = self.clock_sum() if id is None else id
        assert self.id is not None

    def send_event(self,item):
        self.filter.add(str(item))
        self.id = self.clock_sum()

    def receive_event(self,item):
        # print(type(item))
        assert isinstance(item,BloomClock) or isinstance(item,HybridLamportBloom)
        assert item is not self
        clock = self.merge_clocks(self,item)
        return clock

    def get_clock(self):
        return BloomClock(self.size,self.get_filter(),self.id)

    def get_filter(self):
        x = self.filter.get()
        return x

    def set_filter(self,filter):
        assert isinstance(filter,BloomFilter)
        self.filter = filter

    def compare(self, b):
        assert isinstance(b,BloomClock) or isinstance(b,HybridLamportBloom)

        firstBigger = 0
        secondBigger = 0

        filter = self.get_filter()
        other = b.get_filter()

        for i in range(len(filter)):
            #print("iterating filter")
            if filter[i] < other[i]:
                secondBigger += other[i] - filter[i]
            elif filter[i] > other[i]:
                firstBigger += filter[i] - other[i]

        # if filter == other:
        #     print("identical")

        # if filter is other:
            # print(self.id)
            # print(b.id)
            # print("definitely shouldn't be happening")

        if firstBigger != 0 and secondBigger != 0:
            return False, firstBigger, secondBigger

        return True, firstBigger, secondBigger

    def happened_before(self, b):
        comparable, firstBigger, secondBigger = self.compare(b)

        if not comparable:
            # print("not comparable")
            return 1, "clocks not comparable"

        if firstBigger > secondBigger:
            # print("first bigger")
            return 1, "first bigger"

        return self.fp_rate(b), None

    def happened_after(self, b):
        comparable, firstBigger, secondBigger = self.compare(b)

        if not comparable:
            return 1, "clocks not comparable"

        if firstBigger < secondBigger:
            # print("second bigger")
            return 1, "second bigger"

        return self.fp_rate(b), None

    def clock_sum(self):
        filter = self.get_filter()
        sum = 0
        for i in range(len(filter)):
            sum += filter[i]
        # print("printing sum: ",sum)
        return sum

    def fp_rate(self, b):
        sumA = self.clock_sum()
        sumB = b.clock_sum()

        return math.pow(1 - math.pow(1 - (1/self.size), sumB), sumA)

    @staticmethod
    def merge_clocks(a, b):
        assert isinstance(a,BloomClock) or isinstance(a,HybridLamportBloom)
        assert isinstance(b,BloomClock) or isinstance(b,HybridLamportBloom)

        new_filter = []

        _filter = a.get_filter()
        _other = b.get_filter()
        for i in range(len(_filter)):
            if _filter[i] <= _other[i]:
                new_filter.append(_other[i])
            elif _filter[i] > _other[i]:
                new_filter.append(_filter[i])

        # print(a.id)
        # print(b.id)
        id = max(a.id,b.id)
        # print("new id is: ",id)

        return BloomClock(a.size,filter=new_filter,id=id)

    def get_id(self):
        return self.id

    def __repr__(self):
        return self.get_filter()


class HybridLamportBloom(Clock):

    def __init__(self,time=None,lamport=None,bloom=None,hash_count=3,filter_size=50):
        global counter
        self.time = 0 if time is None else time
        self.type = "hybrid-bloom"
        self.lamport = LamportClock() if lamport is None else lamport
        self.hash_count = hash_count
        self.filter_size = filter_size
        self.bloom = BloomClock(hash_count=self.hash_count,filter_size=self.filter_size) if bloom is None else bloom
        self.id = (self.lamport.get_id(),self.bloom.get_id()) if id is None else id

    def send_event(self,item=None):
        self.lamport.send_event()
        self.bloom.send_event(item)

    def receive_event(self,item=None):
        return self.merge(item)

    def merge(self,clock):
        new_lamport = self.lamport.receive_event(clock.lamport)
        new_bloom = self.bloom.receive_event(clock.bloom)
        new_id = (new_lamport.get_id(),new_bloom.get_id())
        return HybridLamportBloom(new_id,new_lamport,new_bloom)

    def get_clock(self):
        return HybridLamportBloom(self.id,self.lamport,self.bloom,self.hash_count,self.filter_size)

    def get_id(self):
        return self.id
