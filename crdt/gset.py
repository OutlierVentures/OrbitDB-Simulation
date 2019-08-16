from crdt.crdt_set import StateCRDT, random_client_id, OperationTuple3
from copy import deepcopy
from collections import MutableSet
from ordered_set import OrderedSet
from time import time
import uuid

class GSet(StateCRDT,OrderedSet):

    def __init__(self, iterable=None,options=None):
        self._payload = OrderedSet() if iterable is None else OrderedSet(iterable)

        # self._operations = [] if iterable is None  \
        #     else map(OperationTuple3.create,iterable)

        self._options = {} if options is None else options

    def merge(self, other):
        assert isinstance(other,GSet)
        print("Pre merge:")
        print(self._payload)
        print(other._payload)
        merged = list(self._payload.union(other._payload))
        # print("*******************      PERFORMING MERGE    ***************")
        # print(merged)
        merged.sort()
        print("--")
        print(merged)
        return GSet(merged)

    def compare(self, other):
        return self.issubset(other)

    # @property
    def values(self):
        return self._payload.__iter__()

    def get_payload(self):
        return list(self._payload)

    def set_payload(self, payload):
        self._payload = OrderedSet(payload)

    def generate_log(self,log):
        assert isinstance(log,GSet)
        return GSet(log.get_payload())

    payload = property(get_payload, set_payload)

    #
    # Set API
    #
    def add(self, element):
        self._payload.add(element)
        temp = list(self._payload)
        temp.sort()
        self._payload = OrderedSet(temp)

    def discard(self, element):
        raise NotImplementedError("This is a grow-only set")

    def __contains__(self, element):
        return self.values.__contains__(element)

    def __iter__(self):
        return self.values.__iter__()

    def __len__(self):
        return self._payload.__len__()




