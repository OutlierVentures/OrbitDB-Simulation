from node import Service, Link
from message import Message

# Messages

class Ping(Message):
    pass

class PingBack(Message):
    pass

class RequestPeers(Message):
    pass

class Hello(Message):
    pass

class PeerList(Message):
    def __init__(self, sender, peers):
        self.sender = sender
        self.data = set(peers)

# Services

class PingHandler(Service):
    def handle_message(self, peer, msg):
        if isinstance(msg, Ping):
            print peer, 'ping received from', msg.sender, peer.env.now
            peer.send(msg.sender, PingBack(peer))
            print peer, 'Pinging backi', msg.sender

class PeerRequestHandler(Service):
    def handle_message(self, peer, msg):
        if isinstance(msg, RequestPeers):
            print peer, 'peer request received', peer.env.now
            reply = PeerList(peer, peer.links.keys())
            peer.send(msg.sender, reply)

class NodeManager(Service):

    ping_interval = 1

    def __init__(self, node):
        self.node = node
        self.last_seen = dict() # peer -> timestamp
        self.env.process(self.run())
        self.active_nodes = set()
        self.inactive_nodes = set()

        def disconnecter(node, other):
            assert node == self.node
            self.inactive_nodes.add(other)
        self.node.disconnecter.append(disconnecter)

    def __repr__(self):
        return "NodeManager(%s)" % self.node.id

    @property
    def env(self):
        return self.node.env

    def handle_message(self, node, msg):
        print msg
        self.last_seen[msg.sender] = self.env.now
        if isinstance(msg, Hello):
            self.recv_hello(msg)
        if isinstance(msg, PeerList):
            self.recv_peerlist(msg)

    def ping_peers(self):
        for l in self.node.links:
            print self.node, 'pinging', l, self.env.now
            if self.env.now - self.last_seen.get(l, 0) > self.ping_interval:
                self.node.send(l, Ping(sender=self.node))

    def recv_hello(self, msg):
        other = msg.sender
        if not other in self.node.links:
            self.node.connect(other)
            self.node.send(other, Hello(self.node))
            self.node.send(other, RequestPeers(self.node))

    def recv_peerlist(self, msg):
        nodes = msg.data
        nodes.discard(self.node)
        self.active_nodes.update(nodes)

    def connect_peer(self, other):
        c = Link(self.env, self.node, other)
        c.send(Hello(self.node), connect=True)

    @property
    def connected_peers(self):
        return self.node.links.keys()

    @property
    def peer_candidates(self):
        candidates = self.active_nodes.difference(set(self.connected_peers))
        return candidates.difference(self.inactive_nodes)

    def run(self):
        while True:
            self.ping_peers()
            yield self.env.timeout(self.ping_interval)
