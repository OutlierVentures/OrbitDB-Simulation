import unittest
import mmh3

from DAG.merkle_dag import Node,DAG

def hash(payload):
    return mmh3.hash(str(payload).encode())

class TestDAGMethods(unittest.TestCase):

    def test_node_constructor(self):
        node = Node("test",2)
        self.assertEqual(node.children,[])
        self.assertEqual(node.hash,hash(2))
        self.assertEqual(node.id,"test")
        self.assertTrue(node.is_leaf())

    def test_dag_constructor(self):
        node1 = Node("one",2)
        node2 = Node("two",3)
        node3 = Node("three",4)
        node4 = Node("parent",5)

        graph = DAG([node1,node2,node3], [node4])

        self.assertFalse(node4.is_leaf())
        self.assertTrue(node2.is_leaf())
        self.assertTrue(node3.is_leaf())
        self.assertTrue(node1.is_leaf())

        self.assertEqual(graph.root,[node4])
        self.assertEqual(graph.root[0].id,"parent")
        x = hash(node4.payload + node1.hash + node2.hash + node3.hash)
        self.assertEqual(graph.root[0].hash,x)

    def test_only_construct_from_leaf(self):
        node1 = Node("one",2)
        node2 = Node("two",3)
        node3 = Node("three",4)
        graph = DAG([node1],[node2])
        self.assertRaises(Exception, DAG,[node2],[node3])

    def test_multi_level_dag(self):
        node1 = Node("one",2)
        node2 = Node("two",3)
        node3 = Node("three",4)

        graph = DAG([node1],[node2])
        graph.add(node3)

        self.assertEqual(len(graph.root),1)
        self.assertEqual(graph.root[0].id,"three")

    def test_multiple_roots(self):
        node1 = Node("one",2)
        node2 = Node("two",3)
        node3 = Node("three",4)
        node4 = Node("four",5)

        graph = DAG([node1],[node2])
        graph.add_multiple([node3,node4])

        self.assertEqual(graph.root,[node3,node4])

    def test_find_hash(self):
        node1 = Node("one",1)
        node2 = Node("two",2)

        graph = DAG([node1],[node2])
        x = hash(node2.payload + node1.hash)
        self.assertEqual(graph.get_node(x),node2)
        x = hash(node1.payload)
        self.assertEqual(graph.get_node(x),node1)

    def test_missing_node(self):
        node1 = Node("one",1)
        node2 = Node("two",2)
        graph = DAG([node1],[node2])
        self.assertEqual(graph.get_node(100),None)

    def test_find_node_large_dag(self):
        node1 = Node("one",1)
        node2 = Node("two",2)
        graph = DAG([node1],[node2])

        temp1 = None
        temp2 = None

        for i in range(1,15):
            j = i + 20
            n1 = Node(str(i),i)
            n2 = Node(str(j),j)
            graph.add_multiple([n1,n2])
            if i == 13:
                temp1 = n1.hash
                temp2 = n1

        self.assertEqual(graph.get_node(100),None)
        self.assertEqual(graph.get_node(temp1),temp2)


if __name__ == '__main__':
    unittest.main()
