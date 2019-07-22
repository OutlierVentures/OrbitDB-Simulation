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

    def get_actives(self):
        return self.active_nodes

    def __repr__(self):
        return "NodeManager(%s)" % self.node.id

    @property
    def env(self):
        return self.node.env

    def handle_message(self, node, msg):
        print msg
        self.last_seen[msg.sender] = self.env.now
        if isinstance(msg, Hello):
            self.receive_hello(msg)
        if isinstance(msg, PeerList):
            self.receive_peerlist(msg)

    # def ping_peers(self):
    #     for l in self.node.links:
    #         self.ping_counter += 1
    #         print "ping number " + str(self.ping_counter)
    #         print self.node, 'pinging', l, self.env.now
    #         #if self.env.now - self.last_seen.get(l, 0) > self.ping_interval:
    #         self.node.send(l, Ping(sender=self.node))
    #
    # def receive_hello(self, msg):
    #     print str(self.node.id) + " receiving hello from " + str(msg.sender.id)
    #     other = msg.sender
    #     if not other in self.node.links:
    #         self.node.connect(other)
    #         self.node.send(other, Hello(self.node))
    #         self.node.send(other, RequestPeers(self.node))

    def receive_peerlist(self, msg):
        nodes = msg.data
        nodes.discard(self.node)
        self.active_nodes.update(nodes)

    def connect_peer(self, other):
        c = self.node.connect(other)
        # c = Link(self.env, self.node, other)
        c.send(Hello(self.node), connect=True)
        print self.node.id + " saying hello to " + other.id

    def network_broadcast(self,msg):
        print "in here"
        nodes = self.get_actives()
        for n in nodes:
            print str(n.id)
            print "broadcasting to node " + n.id
            self.send(n,msg)

    @property
    def connected_peers(self):
        return self.node.links.keys()

    @property
    def peer_candidates(self):
        candidates = self.active_nodes.difference(set(self.connected_peers))
        return candidates.difference(self.inactive_nodes)

    def run(self):
        while True:
            #self.ping_peers()
            self.network_broadcast(Hello(self.node))
            yield self.env.timeout(self.ping_interval)
