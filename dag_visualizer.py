import pydot
from merkle_dag import Node,DAG
from IPython.display import Image, display
from orderedset import OrderedSet

class graph_drawer:

    def __init__(self, graph):
        self._graph = graph
        self._roots = self._graph.root
        self.image = pydot.Dot(graph_type="digraph")
        self.edges = OrderedSet()
        self.nodes = OrderedSet()

    def draw(self):
        self.draw_parents(self._roots)
        im = Image(self.image.create_png())
        with open("test.png", "wb") as fout:
            fout.write(im.data)

    def draw_parents(self,base):
        for r in base:
            node = pydot.Node(r.hash,style ="filled",fillcolor="green")
            print("Node " + str(r.id) + " drawn")
            self.image.add_node(node)
            self.draw_branch(r.links,r.hash)

        for n in self.nodes:
            node = pydot.Node(n,style ="filled",fillcolor="yellow")
            self.image.add_node(node)

        for e in self.edges:
            edge = pydot.Edge(e[0],e[1])
            self.image.add_edge(edge)

    def draw_branch(self,base,parent):
        for r in base:
            #node = pydot.Node(r.id,style ="filled",fillcolor="yellow")
            self.nodes.add(r.hash)
            print("Node " + str(r.id) + " added")
            #self.image.add_node(node)
            self.edges.add((parent,r.hash))
            # edge = pydot.Edge(parent,r.id)
            # self.image.add_edge(edge)
            if r.node.is_leaf():
                continue
            for a in r.node.links:
                print(r.id + "....")
                print(a.id)
            new_roots = r.node.links
            self.draw_branch(new_roots,r.hash)

if __name__ == '__main__':
    node1 = Node("one",2)
    node2 = Node("two",3)
    node3 = Node("three",4)
    node4 = Node("four",5)

    graph = DAG([node1],[node2])
    graph.add_multiple([node3,node4],[node1.hash])

    print("graph completed, now drawing")
    view = graph_drawer(graph)
    view.draw()
