import math
import util

#
# relevance
#

def relevance(target, treatment):
    return util.dot(target,treatment)
#
# disparity
#

def disparity(target, treatment):
    return util.l2(treatment)

#
# ee
#

def ee(target, treatment):
    d = disparity(target,treatment)
    r = relevance(target,treatment)
    l2_target = util.l2(target)
    return d - 2.0*r + l2_target
