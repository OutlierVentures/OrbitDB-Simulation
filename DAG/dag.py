import networkx as nx
import pygraphviz

if __name__ == '__main__':

     G = nx.complete_graph(5)
     A = nx.nx_agraph.to_agraph(G)
     H = nx.nx_agraph.from_agraph(A)
