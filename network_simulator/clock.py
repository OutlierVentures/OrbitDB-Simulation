import random
from abc import ABC, abstractmethod

IDList = []
for i in range(0,1000000):
    IDList.append(i)

def key_generator():
    global IDList
    x = random.choice(IDList)
    IDList.pop(IDList.index(x))
    return x

counter = 1

class Clock(ABC):

    @abstractmethod
    def send_event(self,item=None):
        pass

    @abstractmethod
    def receive_event(self,item=None):
        pass

    @abstractmethod
    def get_clock(self):
        pass

    @abstractmethod
    def get_id(self):
        pass

class LamportClock(Clock):

    def __init__(self,id=None,time=None):
        global counter
        self.time = 0 if time is None else time
        self.id = key_generator() if id is None else id
        self.type = "lamport"

    def send_event(self,item=None):
        self.increment()

    def receive_event(self,item=None):
        return self.merge(item)

    def increment(self):
        self.time += 1

    def merge(self,clock):
        self.time = max(self.time, clock.time) + 1
        self.id = max(self.id,clock.id)
        return LamportClock(self.id, self.time)

    def get_clock(self):
        return LamportClock(self.id,self.time)

    def get_id(self):
        return self.time


