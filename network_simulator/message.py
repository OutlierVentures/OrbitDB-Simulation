class Message(object):
    base_size = 1
    def __init__(self,sender,receiver,sending_time,data=None):
        self.sender = sender
        self.receivers = receiver
        self.data = data
        self.time_sent = sending_time
        self.receive_time = sending_time + 1

    @property
    def size(self):
        return self.base_size + len(repr(self.data))

    def __repr__(self):
        return "message from " + self.sender.id + " sent to " + str(len(self.receivers)) + " nodes; generated at " + str(self.time_sent)
