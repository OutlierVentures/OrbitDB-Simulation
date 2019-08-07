counter = 1

class LamportClock:

    def __init__(self,id=None,time=None):
        global counter
        self.time = 0 if time is None else time
        self.id = counter if id is None else id
        counter += 1

    def increment(self):
        self.time += 1

    def merge(self,clock):
        self.time = max(self.time, clock.time)
        return LamportClock(self.id, self.time)


