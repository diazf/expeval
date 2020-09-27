import math
import util
import metrics
from metrics import Metric

def exposure(exposures, did2gids, qrels=None):
    retval = {}
    for did,gids in did2gids.items():
        if (qrels == None) or ((did in qrels) and (qrels[did] > 0)):
            for gid in gids:
                if not(gid in retval):
                    retval[gid] = 0.0
                if did in exposures:
                    retval[gid] = retval[gid] + exposures[did]
    return retval

def metrics(target, umType, umPatience, umUtility, n, r):
    k = len(target)
    disparity = Metric("disparity", 0.0)
    relevance = Metric("relevance", 1.0)
    difference = Metric("difference", 0.0)
    if (umType == "rbp"):
        disparity.upperBound = disparity_ub_rbp(umPatience, r, k)
        disparity.lowerBound = disparity_lb_rbp(umPatience, r, k)
        relevance.upperBound = relevance_ub_rbp(umPatience, target, r)
        relevance.lowerBound = relevance_lb_rbp(target,umPatience, r)
        difference.upperBound = difference_ub_rbp(umPatience, target, r)
        difference.lowerBound = 0.0
    elif (umType == "gerr"):
        disparity.upperBound = disparity_ub_gerr(umPatience, umUtility, r, k)
        disparity.lowerBound = disparity_lb_gerr(umPatience, umUtility, r, k)
        relevance.upperBound = relevance_ub_gerr(umPatience, umUtility, target, r)
        relevance.lowerBound = relevance_lb_gerr(umPatience, umUtility, target, r)
        difference.upperBound = difference_ub_gerr(umPatience, umUtility, target, r)
        difference.lowerBound = 0.0        
    if (k==1):
        disparity.lowerBound = 0
        disparity.upperBound = 0
    return disparity, relevance, difference
#
# BOUNDS ON GROUP EXPOSURE
#
# NB. these are all quite loose bounds
#

# assume all groups get all of the exposure
def disparity_ub_rbp(p,n,k):
    e = util.geometricSeries(p,n) 
    return e * e * k

# assume all groups get equal exposure
def disparity_lb_rbp(p,n,k):
    return 0.0
    if (n == math.inf):
        return 0.0
    else:
        exposure = util.geometricSeries(p,n)
        return k * exposure * exposure

# assume the all groups get all of the exposure
def relevance_ub_rbp(p,target,n):
    attention_mass = util.geometricSeries(p,n)
    retval = 0.0
    for v in target.values():
        retval = retval + v * attention_mass
    return retval

# assume the least relevant group gets all of the exposure
def relevance_lb_rbp(p,target,n):
    return 0.0
# assume the least relevant group gets all of the exposure
def difference_ub_rbp(p,target,n):
    exposure_mass = util.geometricSeries(p,n)
    #
    # case 1: no exposure to any relevant group
    #
    norm = 0.0
    for d,e in target.items():
        norm = norm + e*e
    #
    # case 2: max exposure to all groups
    #
    retval = 0.0
    dist = []
    diff = 0.0
    for d,e in target.items():
        dist.append(e)
        diff = diff + (exposure_mass-e)*(exposure_mass-e)
    if (norm > diff):
        return norm
    else:
        return diff
    
def disparity_ub_gerr(p,u,n,k):
    return disparity_ub_rbp(p,n,k)
def disparity_lb_gerr(p,u,n,k):
    return disparity_lb_rbp(p*u,n,k)
def relevance_ub_gerr(p,u,target,n):
    return relevance_ub_rbp(p,target,n)
def relevance_lb_gerr(p,u,target,n):
    return relevance_lb_rbp(p*u,target,n)
def difference_ub_gerr(p,u,target,n):
    return difference_ub_rbp(p,target,n)
