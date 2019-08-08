from bloom_clock.bloom_filter import BloomFilter
import math
import copy

class BloomClock:

    def __init__(self,time_iterations,false_positive,filter=None):
        self.size = 40
        self.hash_count = 3
        self.filter = BloomFilter(self.size,self.hash_count)
        if filter is not None:
            if isinstance(filter,BloomFilter):
                self.set_filter(filter)
            else:
                self.filter = BloomFilter(self.size,self.hash_count)
                self.filter.bit_array = filter
        self.time_iterations = time_iterations
        self.false_positive = false_positive

    def send_event(self,item):
        self.filter.add(str(item))

    def receive_event(self,item):
        # print(type(item))
        assert isinstance(item,BloomClock)
        assert item is not self
        clock = self.merge_clocks(self,item)
        return clock

    def get_clock(self):
        return BloomClock(self.size,self.hash_count,self.filter)

    def get_filter(self):
        x = self.filter.get()
        return x

    def set_filter(self,filter):
        assert isinstance(filter,BloomFilter)
        self.filter = filter

    def compare(self, b):
        assert isinstance(b,BloomClock)

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

        if filter == other:
            print("identical")

        if firstBigger != 0 and secondBigger != 0:
            return False, firstBigger, secondBigger

        return True, firstBigger, secondBigger

    def happened_before(self, b):
        comparable, firstBigger, secondBigger = self.compare(b)

        if not comparable:
            print("not comparable")
            return 1, "clocks not comparable"

        if firstBigger > secondBigger:
            print("first bigger")
            return 1, "first bigger"

        return self.fp_rate(b), None

    def happened_after(self, b):
        comparable, firstBigger, secondBigger = self.compare(b)

        if not comparable:
            return 1, "clocks not comparable"

        if firstBigger < secondBigger:
            print("second bigger")
            return 1, "second bigger"

        return self.fp_rate(b), None

    def clock_sum(self):
        filter = self.get_filter()
        sum = 0
        for i in range(len(filter)):
            sum += filter[i]
        return sum

    def fp_rate(self, b):
        sumA = self.clock_sum()
        sumB = b.clock_sum()

        return math.pow(1 - math.pow(1 - 0.5, sumB), sumA)

    @staticmethod
    def merge_clocks(a, b):
        assert isinstance(a,BloomClock)
        assert isinstance(b,BloomClock)

        new_filter = []

        _filter = a.get_filter()
        _other = b.get_filter()
        for i in range(len(_filter)):
            if _filter[i] <= _other[i]:
                new_filter.append(_other[i])
            elif _filter[i] > _other[i]:
                new_filter.append(_filter[i])

        return BloomClock(a.size,a.hash_count,new_filter)

    def __repr(self):
        return self.get_filter()

