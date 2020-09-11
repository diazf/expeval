import util

#
# relevance
#

def relevance(target, treatment, normalized = True):
    r_treatment = util.dot(target,treatment)
    if normalized:
        l2_target = util.l2(target)
        if (l2_target > 0.0):
            return r_treatment / l2_target
        else:
            return float("inf")
    else:
        return r_treatment        
#
# disparity
#

def disparity(target, treatment, normalized = True):
    d_treatment = util.l2(treatment)
    if normalized:
        l2_target = util.l2(target)
        if (l2_target > 0.0):
            return d_treatment / l2_target
        else:
            return float("inf")
    else:
        return d_treatment

#
# ee
#

def ee(target, treatment, normalized = True):
    d = disparity(target,treatment,False)
    r = relevance(target,treatment,False)
    l2_target = util.l2(target)
    return d - 2.0*r + l2_target
