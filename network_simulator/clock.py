import random
from abc import ABC, abstractmethod

from bloom_clock.bloom_clock import BloomClock

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
        self.dag_height = 0

    def send_event(self,item=None):
        self.increment()

    def set_height(self,height):
        self.dag_height = height

    def get_height(self):
        return self.dag_height

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

class HybridLamportBloom(Clock):

    def __init__(self,id=None,lamport=None,bloom=None):
        global counter
        self.time = 0 if time is None else time
        self.type = "lamport"
        self.lamport = LamportClock(self.id) if lamport is None else lamport
        self.bloom = BloomClock() if bloom is None else bloom
        self.id = (self.lamport.get_id(),self.bloom.get_id()) if id is None else id

    def send_event(self,item=None):
        self.lamport.send_event()
        self.bloom.send_event(item)

    def receive_event(self,item=None):
        return self.merge(item)

    def merge(self,clock):
        new_lamport = self.lamport.receive_event(clock)
        new_bloom = self.bloom.receive_event(clock)
        new_id = (new_lamport.get_id(),new_bloom.get_id())
        return HybridLamportBloom(new_id,new_lamport,new_bloom)

    def get_clock(self):
        return HybridLamportBloom(self.id,self.lamport,self.bloom)


