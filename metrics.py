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
    def float(self,normalized = False):
        if normalized:
            if (self.lowerBound == None) or (self.upperBound == None) or (self.lowerBound == self.upperBound):
                return self.defaultValue
            else:
                return self.value / (self.upperBound - self.lowerBound)
        else:
            return self.value
    def string(self,normalized = False):
        v = self.float(normalized)
        return "%f"%v

#
# relevance
#

def relevance(target, run):
    return util.dot(target,run)
#
# disparity
#

def disparity(target, run):
    return util.l2(run,False)

#
# ee
#

def ee(target, run):
    return util.distance(target, run, False)
