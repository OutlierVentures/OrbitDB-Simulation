from abc import ABCMeta, abstractmethod, abstractproperty
from copy import deepcopy
import base64
import random

class OperationTuple3():
    def __init__(self,value,added,removed):
        this.value = value
        this.added = Set(added)
        this.removed = Set(removed)

    def create(value, added, removed):
        new = OperationTuple3(value, added, removed)
        return new

    def from_(js):
        return OperationTuple3.create(js.value,js.added,js.removed)

def random_client_id():
    return 'py_%s' % base64.b64encode(str(random.randint(1, 0x40000000)))


class StateCRDT(object):
    __metaclass__ = ABCMeta

    def __init__(self, iterable=None, options=None):
        self._values = set()

        self._operations = [] if iterable is None  \
            else map(OperationTuple3.create,iterable)

        self._options = {} if options is None else options


    @abstractproperty
    def values(self):
        """Returns the expected value generated from the payload"""
        pass

    @abstractproperty
    def payload(self):
        """This is a deepcopy-able version of the CRDT's payload.
        If the CRDT is going to be serialized to storage, this is the
        data that should be stored.
        """
        pass

    @classmethod
    @abstractmethod
    def merge(cls, X, Y):
        """Merge two replicas of this CRDT"""
        pass

    #
    # Built-in methods
    #

    def __repr__(self):
        return "<%s %s>" % (self.__class__, self.value)

    def clone(self):
        """Create a copy of this CRDT instance"""
        return self.__class__.from_payload(deepcopy(self.payload))

    @classmethod
    def from_payload(cls, payload, *args, **kwargs):
        """Create a new instance of this CRDT using a payload.  This
        is useful for creating an instance using a deserialized value
        from a datastore."""
        new = cls(*args, **kwargs)
        new.payload = payload
        return new
