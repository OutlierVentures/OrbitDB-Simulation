import unittest
import json
from crdt.gset import GSet
from crdt.crdt_set import StateCRDT

class TestGSetMethods(unittest.TestCase):

    def test_constructor(self):
        crdt = GSet()
        self.assertNotEqual(crdt, None)
        self.assertNotEqual(crdt._payload, None)
        self.assertTrue(isinstance(crdt._payload, set))

    def test_isCmRDTSet(self):
        crdt = GSet()
        self.assertTrue(isinstance(crdt, StateCRDT))

    def test_creates_set_from_values(self):
        crdt = GSet(['A','B'])
        self.assertNotEqual(crdt, None)
        self.assertTrue(isinstance(crdt._payload, set))
        self.assertEqual(crdt._payload, set(['A','B']))

    def test_iterator_type(self):
        crdt = GSet()
        self.assertTrue(isinstance(crdt.values(), type(set().__iter__())))

    def test_iterator_functionality(self):
        crdt = GSet()
        crdt.add('A')
        crdt.add('B')
        iterator = crdt.values()
        self.assertEqual(iterator.next(), 'A')
        self.assertEqual(iterator.next(), 'B')

    def test_adding_to_crdt(self):
        crdt = GSet()
        crdt.add('A')
        self.assertEqual(set(crdt.values()),set(['A']))

    def test_adding_multiple(self):
        crdt = GSet()
        crdt.add('A')
        crdt.add('B')
        crdt.add('C')
        self.assertEqual(set(crdt.values()),set(['A','B','C']))

    def test_only_unique_items(self):
        crdt = GSet()
        crdt.add(1)
        crdt.add('A')
        crdt.add('A')
        crdt.add(1)
        crdt.add('A')
        obj = { "hello": 'ABC' }
        crdt.add(json.dumps(obj))
        crdt.add(json.dumps(obj))
        crdt.add(json.dumps({ "hello": 'ABCD' }))

        expectedResult = ['A', 1, json.dumps({ "hello": 'ABC' }),json.dumps({ "hello": 'ABCD' })]
        self.assertEqual(set(crdt.values()), set(expectedResult))

    def test_no_removal(self):
        crdt = GSet()
        crdt.add('A')
        try:
            crdt.discard('A')
        except NotImplementedError as error:
            s = error.message

        self.assertEqual(s,"This is a grow-only set")
        self.assertEqual(set(crdt.values()),set(['A']))

    # def test_merge(self):
    #     crdt1 = GSet()
    #     crdt2 = GSet()
    #     crdt1.add('A')
    #     crdt2.add('B')
    #     crdt2.add('C')
    #     crdt1 = crdt1.merge(crdt2)
    #     self.assertEqual(list(crdt1.values()), ['A', 'B', 'C'])

    def test_merge_same_set(self):
        crdt1 = GSet()
        crdt2 = GSet()
        crdt1.add('A')
        crdt2.add('A')
        crdt1 = crdt1.merge(crdt2)
        self.assertEqual(list(crdt1.values()), ['A'])
    #
    # def test_merge_four_sets(self):
    #     crdt1 = GSet()
    #     crdt2 = GSet()
    #     crdt3 = GSet()
    #     crdt4 = GSet()
    #     crdt1.add('A')
    #     crdt2.add('B')
    #     crdt3.add('C')
    #     crdt4.add('D')
    #
    #     crdt1 = crdt1.merge(crdt2)
    #     crdt1 = crdt1.merge(crdt3)
    #     crdt1 = crdt1.merge(crdt4)
    #
    #     self.assertEqual(list(crdt1.values()), ['A', 'B', 'C', 'D'])

    def test_no_overwrite_on_merge(self):
        a = OrderedSet()
        a.add('A')
        a.add('Z')
        a.add('B')
        print(a)
        crdt1 = GSet()
        crdt2 = GSet()
        crdt1.add('A')
        crdt2.add('B')
        crdt1 = crdt1.merge(crdt2)
        print(crdt1._payload)
        crdt1.add('AA')
        crdt2.add('BB')
        crdt1 = crdt1.merge(crdt2)
        print(crdt1._payload)
        self.assertEqual(crdt1._payload, ['A', 'B', 'AA', 'BB'])
        self.assertEqual(crdt2._payload, ['B', 'BB'])





if __name__ == '__main__':
    unittest.main()



#       it('doesn\'t overwrite other\'s values on merge', () => {
#         const crdt1 = new GSet()
#         const crdt2 = new GSet()
#         crdt1.add('A')
#         crdt2.add('B')
#         crdt1.merge(crdt2)
#         crdt1.add('AA')
#         crdt2.add('BB')
#         crdt1.merge(crdt2)
#         assert.deepEqual(crdt1.toArray(), ['A', 'B', 'AA', 'BB'])
#         assert.deepEqual(crdt2.toArray(), ['B', 'BB'])
#       })
#     })
#
#     describe('has', () => {
#       it('returns true if given element is in the set', () => {
#         const crdt = new GSet()
#         crdt.add('A')
#         crdt.add('B')
#         crdt.add(1)
#         const obj = { hello: 'world' }
#         crdt.add(obj)
#         assert.equal(crdt.has('A'), true)
#         assert.equal(crdt.has('B'), true)
#         assert.equal(crdt.has(1), true)
#         assert.equal(crdt.has(obj), true)
#       })
#
#       it('returns false if given element is not in the set', () => {
#         const crdt = new GSet()
#         crdt.add('A')
#         crdt.add('B')
#         assert.equal(crdt.has('nothere'), false)
#       })
#     })
#
#     describe('hasAll', () => {
#       it('returns true if all given elements are in the set', () => {
#         const crdt = new GSet()
#         crdt.add('A')
#         crdt.add('B')
#         crdt.add('C')
#         crdt.add('D')
#         assert.equal(crdt.hasAll(['D', 'A', 'C', 'B']), true)
#       })
#
#       it('returns false if any of the given elements are not in the set', () => {
#         const crdt = new GSet()
#         crdt.add('A')
#         crdt.add('B')
#         crdt.add('C')
#         crdt.add('D')
#         assert.equal(crdt.hasAll(['D', 'A', 'C', 'B', 'nothere']), false)
#       })
#     })
#
#     describe('toArray', () => {
#       it('returns the values of the set as an Array', () => {
#         const crdt = new GSet()
#         const array = crdt.toArray()
#         assert.equal(Array.isArray(array), true)
#       })
#
#       it('returns values', () => {
#         const crdt = new GSet()
#         crdt.add('A')
#         crdt.add('B')
#         const array = crdt.toArray()
#         assert.equal(array[0], 'A')
#         assert.equal(array[1], 'B')
#       })
#     })
#
#     describe('toJSON', () => {
#       it('returns the set as JSON object', () => {
#         const crdt = new GSet()
#         crdt.add('A')
#         assert.equal(crdt.toJSON().values.length, 1)
#         assert.equal(crdt.toJSON().values[0], 'A')
#       })
#
#       it('returns a JSON object after a merge', () => {
#         const crdt1 = new GSet()
#         const crdt2 = new GSet()
#         crdt1.add('A')
#         crdt2.add('B')
#         crdt1.merge(crdt2)
#         crdt2.merge(crdt1)
#         assert.equal(crdt1.toJSON().values.length, 2)
#         assert.equal(crdt1.toJSON().values[0], 'A')
#         assert.equal(crdt1.toJSON().values[1], 'B')
#       })
#     })
#
#     describe('isEqual', () => {
#       it('returns true for sets with same values', () => {
#         const crdt1 = new GSet()
#         const crdt2 = new GSet()
#         crdt1.add('A')
#         crdt2.add('A')
#         assert.equal(crdt1.isEqual(crdt2), true)
#         assert.equal(crdt2.isEqual(crdt1), true)
#       })
#
#       it('returns true for empty sets', () => {
#         const crdt1 = new GSet()
#         const crdt2 = new GSet()
#         assert.equal(crdt1.isEqual(crdt2), true)
#         assert.equal(crdt2.isEqual(crdt1), true)
#       })
#
#       it('returns false for sets with different values', () => {
#         const crdt1 = new GSet()
#         const crdt2 = new GSet()
#         crdt1.add('A')
#         crdt2.add('B')
#         assert.equal(crdt1.isEqual(crdt2), false)
#         assert.equal(crdt2.isEqual(crdt1), false)
#       })
#     })
#   })
# })
