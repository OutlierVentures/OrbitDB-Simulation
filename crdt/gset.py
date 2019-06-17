from crdt_set import StateCRDT, random_client_id, OperationTuple3
from copy import deepcopy
from collections import MutableSet
from time import time
import uuid


class SetStateCRDT(StateCRDT, MutableSet):

    def __contains__(self, element):
        return self.value.__contains__(element)

    def __iter__(self):
        return self.values.__iter__()

    def __len__(self):
        return self.value.__len__()


class GSet(SetStateCRDT):

    def __init__(self, iterable=None,options=None):
        self._payload = set() if iterable is None else set(iterable)

        # self._operations = [] if iterable is None  \
        #     else map(OperationTuple3.create,iterable)

        self._options = {} if options is None else options

    def merge(self, other):

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
        self._payload = set(payload)

    payload = property(get_payload, set_payload)

    #
    # Set API
    #
    def add(self, element):
        self._payload.add(element)

    def discard(self, element):
        raise NotImplementedError("This is a grow-only set")
