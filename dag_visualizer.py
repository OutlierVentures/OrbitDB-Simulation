import pydot
from merkle_dag import Node,DAG
from IPython.display import Image, display

class graph_drawer:

    def __init__(self, graph):
        self._graph = graph
        self._roots = self._graph.root
        self.image = pydot.Dot(graph_type="digraph")
        self.edges = set()

    def draw(self):
        self.draw_parents(self._roots)
        im = Image(self.image.create_png())
        with open("test.png", "wb") as fout:
            fout.write(im.data)

    def draw_parents(self,base):
        for r in base:
            node = pydot.Node(r.id,style ="filled",fillcolor="green")
            print("Node " + str(r.id) + " drawn")
            self.image.add_node(node)
            self.draw_branch(r.links,r.id)

        for e in self.edges:
            edge = pydot.Edge(e)
            self.image.add_edge(edge)

    def draw_branch(self,base,parent):
        for r in base:
            node = pydot.Node(r.id,style ="filled",fillcolor="yellow")
            print("Node " + str(r.id) + " drawn")
            self.image.add_node(node)
            self.edges.add((parent,r.id))
            # edge = pydot.Edge(parent,r.id)
            # self.image.add_edge(edge)
            if r.links is None:
                return
            new_roots = r.links
            self.draw_branch(new_roots,r.id)



if __name__ == '__main__':
    # node1 = Node("one",2)
    # node2 = Node("two",3)
    # node3 = Node("three",4)
    # node4 = Node("four",5)
    # node5 = Node("six",6)
    # node6 = Node("seven",7)
    # node7 = Node("eight",8)
    #
    # graph = DAG([node1,node5],[node2])
    # graph.add_multiple([node3,node4,node6])
    # graph.add(node7)

    node1 = Node("one",1)
    node2 = Node("two",2)
    graph = DAG([node1],[node2])

    for i in range(1,15):
            j = i
            print("adding " + str(i))
            graph.add_multiple([Node(str(i),1),Node(str(j),1)])

    print("graph completed, now drawing")
    view = graph_drawer(graph)
    view.draw()
