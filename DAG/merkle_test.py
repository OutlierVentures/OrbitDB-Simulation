import unittest
from DAG.merkle_dag import Node,DAG


class TestDAGMethods(unittest.TestCase):
    #
    # def test_node_constructor(self):
    #     node = Node("test",2)
    #     self.assertEqual(node.links,[])
    #     self.assertEqual(node.hash,hash(2))
    #     self.assertEqual(node.id,"test")
    #     self.assertTrue(node.is_leaf())
    #
    # def test_dag_constructor(self):
    #     node1 = Node("one",2)
    #     node2 = Node("two",3)
    #     node3 = Node("three",4)
    #     node4 = Node("parent",5)
    #
    #     graph = DAG([node1,node2,node3], [node4])
    #
    #     self.assertFalse(node4.is_leaf())
    #     self.assertTrue(node2.is_leaf())
    #     self.assertTrue(node3.is_leaf())
    #     self.assertTrue(node1.is_leaf())
    #
    #     self.assertEqual(graph.root,[node4])
    #     self.assertEqual(graph.root[0].id,"parent")
    #     x = hash(node4.payload + node1.hash + node2.hash + node3.hash)
    #     self.assertEqual(graph.root[0].hash,x)
    #
    # def test_only_construct_from_leaf(self):
    #     node1 = Node("one",2)
    #     node2 = Node("two",3)
    #     node3 = Node("three",4)
    #     graph = DAG([node1],[node2])
    #     self.assertRaises(Exception,DAG,[node2],[node3])
    #
    # def test_multi_level_dag(self):
    #     node1 = Node("one",2)
    #     node2 = Node("two",3)
    #     node3 = Node("three",4)
    #
    #     graph = DAG([node1],[node2])
    #     graph.add(node3,[node1.hash,node2.hash])
    #
    #     self.assertEqual(len(graph.root),1)
    #     self.assertEqual(graph.root[0].id,"three")
    #
    # def test_multiple_roots(self):
    #     node1 = Node("one",2)
    #     node2 = Node("two",3)
    #     node3 = Node("three",4)
    #     node4 = Node("four",5)
    #
    #     graph = DAG([node1],[node2])
    #     graph.add_multiple([node3,node4],[node1.hash])
    #
    #     self.assertEqual(graph.root,[node2,node3,node4])
    #
    # def test_find_hash(self):
    #     node1 = Node("one",1)
    #     node2 = Node("two",2)
    #
    #     graph = DAG([node1],[node2])
    #     x = hash(node2.payload + node1.hash)
    #     self.assertEqual(graph.get_node(x),node2)
    #     x = hash(node1.payload)
    #     self.assertEqual(graph.get_node(x),node1)
    #
    # def test_missing_node(self):
    #     node1 = Node("one",1)
    #     node2 = Node("two",2)
    #     graph = DAG([node1],[node2])
    #     self.assertEqual(graph.get_node(100),None)

    def test_find_node_large_dag(self):
        node1 = Node("one",1)
        node2 = Node("two",2)
        graph = DAG([node1],[node2])

        for i in range(1,15):
            j = i + 20
            graph.add_multiple([Node(str(i),1),Node(str(j),1)],[graph.root[0].hash])
            #if i == 13:
            for r in graph.root:
                #if r.id == "13":
                print("printing")
                print(r.hash)

        for i in range (1,10000):
            x = graph.get_node(i)
            if x is not None:
                print(x.id)

        self.assertEqual(graph.get_node(100),None)

        self.assertEqual(graph.get_node(18).id,"13")




if __name__ == '__main__':
    unittest.main()
