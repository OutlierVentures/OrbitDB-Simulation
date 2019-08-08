from abc import ABC, abstractmethod

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

class LamportClock(Clock):

    def __init__(self,id=None,time=None):
        global counter
        self.time = 0 if time is None else time
        self.id = counter if id is None else id
        counter += 1
        self.type = "lamport"

    def send_event(self,item=None):
        self.increment()

    def receive_event(self,item=None):
        self.increment()
        return self.merge(item)

    def increment(self):
        self.time += 1

    def merge(self,clock):
        self.time = max(self.time, clock.time)
        return LamportClock(self.id, self.time)

    def get_clock(self):
        return self


