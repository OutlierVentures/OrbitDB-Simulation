
# Hashing functions.
def hash(a):
    return 2*a

class Node:

    def __init__(self,id,value=0,children=None):
        self.id = id
        self.payload = value
        self.links = []
        hash_sum = 0
        if not children is None:
            for c in children:
                hash_sum += c.hash
        self.hash = hash(hash_sum + self.payload)

    def add_link(self,nodes):
        for n in nodes:
            self.links.append(n)
        hash_sum = 0
        for l in self.links:
            hash_sum += l.hash
        self.hash = hash(hash_sum + self.payload)

    def is_leaf(self):
        return True if len(self.links) is 0 else False


class DAG:

    def __init__(self, leaves, parents):
        self.root = []
        self.leaves = []
        self.height = 0
        for l in leaves:
            if len(l.links) is not 0:
                raise Exception('cannot construct dag from a non-leaf node')
                self.leaves = []
                return
            self.leaves.append(l)
            for p in parents:
                p.add_link([l])
        for p in parents:
            self.root.append(p)

    def add(self,node):
        for r in self.root:
            node.add_link([r])
        self.root = []
        self.root.append(node)

    def add_multiple(self,nodes):
        for r in self.root:
            for n in nodes:
                n.add_link([r])
        self.root = []
        for n in nodes:
            self.root.append(n)

    def get_node(self,hash):
        target = None
        for r in self.root:
            if r.hash is hash:
                return r
            for l in r.links:
                target = self.find_node(hash,l)
                if target is not None:
                    return target

        print("the node with that hash cannot be found")
        return None

    def find_node(self,hash,node):
        if node.hash == hash:
            return node
        if node.is_leaf():
            return None
        for l in node.links:
            target = self.find_node(hash,l)
            if target is not None:
                return target

if __name__ == '__main__':
    node1 = Node("one",2)
    node2 = Node("two",3)
    node3 = Node("three",4)



    graph = DAG([node1,node2,node3],Node("parent"),4)

    for n in graph.root:
        print(n.hash)
