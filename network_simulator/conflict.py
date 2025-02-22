import sys
sys.path.append("~/hb2917/")

from collections import Iterable
from network_simulator.message import Message

class Conflict:

    def __init__(self, messages,type=None):
        assert isinstance(messages, Iterable)
        for m in messages:
            assert isinstance(m, Message)

        self.messages = messages
        self.len = len(self.messages)
        self.comparisons = 1 if self.len == 2 else (self.len*(self.len - 1))/2
        self.type = type

        # print(self.len)
        # print(self.comparisons)

        self.incorrect_classifications = 0
        self.correct_classifications = 0

        if self.all_events_classified_concurrent() and self.all_events_concurrent():
            self.correct_classifications = self.comparisons
            self.incorrect_classifications = 0

        else:
            self.find_incorrect_classifications()

    def all_events_classified_concurrent(self):
        if self.type == "bloom":
            for m in self.messages:
                for l in self.messages:
                    # print(m.clock.get_filter(),l.clock.get_filter())
                    if m is l:
                        continue
                    elif m.clock.happened_before(l.clock)[0] == 1 or m.clock.happened_after(l.clock)[0] == 1:
                        continue
                    else:
                        return False


        else:
            for m in self.messages:
                for l in self.messages:
                    if m is l:
                        continue
                    else:
                        if m.clock.time == l.clock.time and m.id == l.id:
                            continue
                        else:
                            return False

        # print("all events are seemingly concurrent")
        return True

    def all_events_concurrent(self):

        # print(self.messages)
        for m in self.messages:
            for l in self.messages:
                if m is l:
                    continue
                else:
                    if m.time_sent == l.time_sent:
                        continue
                    else:
                        # print("none concurrent events")
                        return False

        return True

    def find_incorrect_classifications(self):
        for m in self.messages:
            index = self.messages.index(m)
            counter = index + 1
            while counter < self.len:
                m_comparison = self.messages[counter]
                if self.is_incorrect_pair(m, m_comparison):
                    self.incorrect_classifications += 1
                counter += 1

        self.correct_classifications = self.comparisons - self.incorrect_classifications
        # print("adding in " + str(self.correct_classifications) + " correct classifications")
        # print(self.messages)
        # print("adding in " + str(self.incorrect_classifications) + " incorrect classifications")

    @staticmethod
    def is_incorrect_pair(a,b):
        if a.time_sent > b.time_sent:
            return True
        return False
