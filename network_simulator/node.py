import simpy
import random
from message import Message

class Link(object):

    def __init__(self, env, sender, receiver):
        self.env = env
        self.sender = sender
        self.receiver = receiver
        self.start = env.now
        print "link created between " + str(self.sender.id) + " and "  + str(self.receiver.id) + " at time " + str(self.start)

    def __repr__(self):
        return "Connection between " + str(self.sender) + " -> " + str(self.receiver)

    @property
    def bandwidth(self):
        return min(self.sender.up, self.receiver.down)

    def transfer(self,msg):
        size = msg.size
        delay = self.sender.up + self.receiver.down
        yield self.env.timeout(delay)
        if self.receiver.is_connected(msg.sender):
            self.receiver.messages.put(msg)

    def send(self, msg,connect=True):
        self.env.process(self.transfer(msg))

class Service(object):
    def handle_message(self, receiving_peer, msg):
        pass

class Node(object):


    def __init__(self,id,env):
        self.id = id
        self.env = env
        self.messages = simpy.Store(env)
        self.links = dict()
        self.is_active = True
        self.properties = []
        self.disconnecter = []
        self.node_finder = None
        self.up = random.randint(1,10)
        self.down = random.randint(1,self.up)

        env.process(self.run())

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    def connect(self, node):
        if not self.is_connected(node):
            print(str(self.id) + " connecting to " + str(node.id))
            self.links[node] = Link(self.env, self, node)
            if not node.is_connected(self):
                node.connect(self)

        return self.links[node]

    def disconnect(self, node):
        if self.is_connected(node):
            print(self.id + " disconnecting from " + node.id)
            del self.connections[other]
            if node.is_connected(self):
                node.disconnect(self)
            for d in self.disconnecter:
                d(self, node)

    def is_connected(self, node):
        return node in self.links

    def receive(self, msg):
        assert isinstance(msg, Message)
        for s in self.properties:
            assert isinstance(s, Service)
            s.handle_message(self, msg)

    def send(self,node,msg):
        assert msg.sender == self
        self.links[node].send(msg)

    def broadcast(self, msg):
        for l in self.links:
            self.send(l, msg)

    def run(self):
        while True:
            msg = yield self.messages.get()
            self.receive(msg)
