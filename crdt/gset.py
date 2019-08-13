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
        merged = GSet(self._payload.union(other._payload))

        return merged

    def compare(self, other):
        return self.issubset(other)

    # @property
    def values(self):
        return self._payload.__iter__()

    def get_payload(self):
        return list(self._payload)

    def set_payload(self, payload):
        self._payload = OrderedSet(payload)


    payload = property(get_payload, set_payload)

    #
    # Set API
    #
    def add(self, element):
        self._payload.add(element)

    def discard(self, element):
        raise NotImplementedError("This is a grow-only set")

    def union(self, *sets):
        difference = OrderedSet()

        for s in sets:
            difference.add(self - s)

        difference = sorted(list(difference))

        merged = list(self) + difference
        sorted(merged)

        return merged

    def __contains__(self, element):
        return self.values.__contains__(element)

    def __iter__(self):
        return self.values.__iter__()

    def __len__(self):
        return self._payload.__len__()




