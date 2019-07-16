class Message(object):
    base_size = 1
    def __init__(self, sender, data=None):
        self.sender = sender
        self.data = data

    @property
    def size(self):
        return self.base_size + len(repr(self.data))

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
