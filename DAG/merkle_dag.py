import random

import networkx as nx
import mmh3
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt

class Node:

    hash = None

    def __init__(self,id,value=None):
        self.id = id
        self.payload = value if value is not None else 0
        self.children = []
        self.set_hash()
        self.dag_height = 0

    def add_children(self, child):
        for c in child:
            self.children.append(c)
        self.set_hash()

    def set_hash(self):
        if len(self.children) == 0:
            self.hash = self.hasher(self.payload)
        else:
            hash_sum = 0
            for c in self.children:
                hash_sum += c.hash
            self.hash = self.hasher(hash_sum + self.payload)

    def is_leaf(self):
        return True if len(self.children) is 0 else False

    @staticmethod
    def hasher(payload):
        return mmh3.hash(str(payload).encode())

    def set_height(self,height):
        self.dag_height = height

    def get_hash(self):
        return self.hash

    def __repr__(self):
        return str(self.hash)

class DAG:

    def __init__(self, leaves, parents=None):
        self.graph = nx.DiGraph()
        self.root = []
        self.leaves = []
        self.height = 0

        self.graph.add_nodes_from(leaves)
        self.leaves = leaves

        self.hash_map = {}

        for l in leaves:
            if len(l.children) is not 0:
                raise Exception('cannot construct dag from a non-leaf node')
                self.leaves = []
                return

        if parents is not None:
            self.height += 1
            self.graph.add_nodes_from(parents)
            for l in self.leaves:
                l.set_height(self.height - 1)
                self.add_to_hashmap(l)
                for p in parents:
                    self.graph.add_edge(p,l)

            for p in parents:
                p.add_children(self.leaves)
                p.set_height(self.height)
                self.root.append(p)
                self.add_to_hashmap(p)

    def add(self,node):
        self.height += 1
        self.graph.add_node(node)

        for r in self.root:
            self.graph.add_edge(node,r)

        node.add_children(self.root)
        node.set_height(self.height)
        self.add_to_hashmap(node)
        self.root = [node]

    def add_multiple(self,nodes):
        self.height += 1
        for r in self.root:
            for n in nodes:
                self.graph.add_node(n)
                self.graph.add_edge(n,r)
                n.set_height(self.height)

        for n in nodes:
            n.add_children(self.root)
            self.add_to_hashmap(n)

        self.root = nodes

    def add_to_hashmap(self,node):
        self.hash_map[node.get_hash()] = node

    def get_node(self,hash):
        node = self.hash_map.get(hash)
        if node is None:
            print("hash is not present in DAG")

        return node

    def merge(self,dag):
        for r in self.root:
            if dag.has_hash(r.hash):
                return dag

        for r in dag.root:
            if self.has_hash(r.hash):
                return self

        node = Node("something" + str(id(self)))
        graph = nx.DiGraph()
        graph.add_edges_from(list(self.graph.edges()) + list(dag.graph.edges()))
        graph.add_nodes_from(list(self.graph.nodes()) + list(dag.graph.nodes()))

        self.root = dag.root + self.root
        self.height = max(self.height,dag.height)

        if not nx.is_directed_acyclic_graph(graph):
            print("Cannot do this operation as it would not be a DAG!")
            return
        else:
            self.root = dag.root + self.root
            self.height = max(self.height, dag.height)
            self.graph = graph
            self.add(node)

    def has_hash(self,hash):
        if self.hash_map.get(hash) is None:
            return False
        return True

if __name__ == '__main__':
    node1 = Node("one",2)
    node2 = Node("two",3)
    node3 = Node("three",4)

    _node1 = Node("_one",9)
    _node2 = Node("_two",399)
    _node3 = Node("_three",4999)

    graph = DAG([node1,node2,node3],[Node("parent",5)])
    _graph = DAG([_node1,_node2,_node3],[Node("__parent",50)])

    graph.add_multiple([Node("parent2",12),Node("parent3",54)])

    graph.merge(_graph)

    assert nx.is_directed_acyclic_graph(graph.graph)

    for n in graph.root:
        print(n.hash)

    print(graph.height)

    for g in graph.graph.nodes():
        print(g.hash)


    # write_dot(graph.graph, 'test.dot')

    # same layout using matplotlib with no labels
    # plt.title('draw_networkx')
    # pos = graphviz_layout(G, prog='dot')
    # nx.draw(G, pos, with_labels=False, arrows=False)
    # plt.savefig('nx_test.png')

    p = nx.drawing.nx_pydot.to_pydot(graph.graph)
    p.write_png('example.png')
    # pos = hierarchy_pos(graph.graph,graph.root)
    # nx.draw_networkx_nodes(graph.graph, pos, ax=None)
    # nx.draw_networkx_edges(graph.graph, pos, ax=None)
    # plt.axis('off')
    # plt.show()
