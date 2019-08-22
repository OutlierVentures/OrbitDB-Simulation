import copy
import math
import mmh3

class BloomFilter(object):

    def __init__(self, size, hash_functions):
        '''
        items_count : int
            Number of items expected to be stored in bloom filter
        fp_prob : float
            False Positive probability in decimal
        '''

        # Size of bit array to use
        self.size = size

        # number of hash functions to use
        self.hash_count = hash_functions
        # print("hash count is: " + str(self.hash_count))

        # Bit array of given size
        self.bit_array = [0] * self.size
        # print("size is: ",self.size)

        # self.fp_prob


    def add(self, item):
        '''
        Add an item in the filter
        '''
        digests = []
        for i in range(self.hash_count):
            # create digest for given item.
            # i work as seed to mmh3.hash() function
            # With different seed, digest created is different
            # print(self.size)
            digest = mmh3.hash(item, i) % self.size
            digests.append(digest)

            # Increment index in bit_array
            # print("incrementing index: " + str(digest))
            self.bit_array[digest] +=1

    def check(self, item):
        '''
        Check for existence of an item in filter
        '''
        for i in range(self.hash_count):
            digest = mmh3.hash(item, i) % self.size
            if self.bit_array[digest] == 0:
                # if any of bit is False then,its not present
                # in filter
                # else there is probability that it exist
                return False
        return True

    def get(self):
        return copy.copy(self.bit_array)

    # def __iter__(self):
    #     self.x = self.bit_array[0]
    #     return self
    #
    # def __next__(self):
    #     x = self.x
    #     i = self.bit_array.index(x)
    #
    #     if i >= len(self.bit_array):
    #         raise StopIteration
    #
    #     self.x = self.bit_array[i+1]
    #     return x

    # @classmethod
    # def get_size(self, n, p):
    #     '''
    #     Return the size of bit array(m) to used using
    #     following formula
    #     m = -(n * lg(p)) / (lg(2)^2)
    #     n : int
    #         number of items expected to be stored in filter
    #     p : float
    #         False Positive probability in decimal
    #     '''
    #     m = -(n * math.log(p)) / (math.log(2) ** 2)
    #     return int(m)
    #
    # @classmethod
    # def get_hash_count(self, m, n):
    #     '''
    #     Return the hash function(k) to be used using
    #     following formula
    #     k = (m/n) * lg(2)
    #
    #     m : int
    #         size of bit array
    #     n : int
    #         number of items expected to be stored in filter
    #     '''
    #     k = (m / n) * math.log(2)
    #     return int(k)