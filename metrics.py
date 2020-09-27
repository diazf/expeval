import math
import util
#
# metric class to hold raw metric value and supporting data
#
class Metric:
    def __init__(self, name, defaultValue):
        self.name = name
        self.lowerBound = None
        self.upperBound = None
        self.defaultValue = defaultValue
        self.value = 0
    def get(self,normalized = False):
        if normalized:
            if (self.lowerBound == None) or (self.upperBound == None) or (self.lowerBound == self.upperBound):
                return self.defaultValue
            else:
                return self.value / (self.upperBound - self.lowerBound)
        else:
            return self.value

#
# relevance
#

def relevance(target, treatment):
    return util.dot(target,treatment)
#
# disparity
#

def disparity(target, treatment):
    return util.l2(treatment,False)

#
# ee
#

def ee(target, treatment):
    return util.distance(target, treatment, False)
