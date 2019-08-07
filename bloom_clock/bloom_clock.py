from bloom_clock.bloom_filter import BloomFilter
import math
import copy

class BloomClock:

    def __init__(self,time_iterations,false_positive,filter=None):
        self.filter = BloomFilter(time_iterations*10,false_positive)
        if filter is not None:
            self.set_filter(filter)
        self.time_iterations = time_iterations
        self.false_positive = false_positive

    def send_event(self,item):
        self.filter.add(str(item))

    def receive_event(self,item):
        print(type(item))
        clock = self.merge_clocks(item)
        return clock

    def get_filter(self):
        return self.filter.bit_array

    def set_filter(self,array):
        self.filter.bit_array = array

    def compare(self, b):
        assert isinstance(b,BloomClock)

        firstBigger = 0
        secondBigger = 0

        filter = self.get_filter()
        other = b.get_filter()

        for i in range(len(filter)):
            if filter[i] < other[i]:
                secondBigger += other[i] - filter[i]
            elif filter[i] > other[i]:
                firstBigger += filter[i] - other[i]

        if firstBigger != 0 and secondBigger != 0:
            return False, firstBigger, secondBigger

        return True, firstBigger, secondBigger

    def happened_before(self, b):
        comparable, firstBigger, secondBigger = self.compare(b)

        if not comparable:
            return 1, "clocks not comparable"

        if firstBigger > secondBigger:
            return True, 1, "first bigger"

        return self.fp_rate(b), None

    def happened_after(self, b):
        comparable, firstBigger, secondBigger = self.compare(b)

        if not comparable:
            return 1, "clocks not comparable"

        if firstBigger < secondBigger:
            return True, 1, "second bigger"

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

    def merge_clocks(self, b):
        new_filter = []

        filter = self.get_filter()
        other_filter = b.get_filter()
        for i in range(len(filter)):
            if filter[i] <= other_filter[i]:
                new_filter.append(other_filter[i])
            elif filter[i] > other_filter[i]:
                new_filter.append(filter[i])

        clock = copy.copy(self)
        clock.set_filter(new_filter)

        return clock

    def __repr(self):
        return self.get_filter()

