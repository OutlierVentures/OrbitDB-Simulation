
class Disruption:

    def __init__(self,node,start_time,end_time):
        self.node = node
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return "dropout to " + self.node.id + " from " + str(self.start_time) + " to " + str(self.end_time)
