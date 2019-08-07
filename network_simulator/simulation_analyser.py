from network_simulator.conflict import Conflict

class SimulationAnalyser:

    def __init__(self):
        self.total_conflicts = 0
        self.correct = 0
        self.incorrect = 0

    def record_conflict(self,conflict):
        self.total_conflicts += conflict.comparisons
        self.correct += conflict.correct_classifications
        self.incorrect += conflict.incorrect_classifications

    def get_results(self):
        print("******** SIMULATION RESULTS *************")
        print ("Total conflicts = " + str(self.total_conflicts))
        print("Correct classifications = " + str(self.correct))
        print("Incorrect classifcations = " + str(self.incorrect))

        percent_correct = (self.correct/self.total_conflicts) * 100
        print("Algorithm performance: " + str(percent_correct) + "%")






