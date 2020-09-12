import math
import util

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

def treatment_exposures(exposures, did2gids, qrels):
    return exposure(exposures, did2gids, qrels)

def target_exposures(exposures, did2gids, qrels, umType, umPatience, umUtility, complete):
    target = exposure(exposures, did2gids, qrels)
    n = len(exposures) if (complete) else math.inf
    k = len(target)
    r = 0
    for v in qrels.values():
        if (v>0):
            r = r + 1
    disparity_lb = 0.0
    disparity_ub = 0.0
    relevance_lb = 0.0
    relevance_ub = 0.0
    difference_lb = 0.0
    difference_ub = 0.0
    if (umType == "rbp"):
        disparity_ub = disparity_ub_rbp(umPatience, r, k)
        disparity_lb = disparity_lb_rbp(umPatience, r, k)
        relevance_ub = relevance_ub_rbp(umPatience, target, r)
        relevance_lb = relevance_lb_rbp(target,umPatience, r)
        difference_ub = difference_ub_rbp(umPatience, target, r)
    elif (umType == "gerr"):
        disparity_ub = disparity_ub_gerr(umPatience, umUtility, r, k)
        disparity_lb = disparity_lb_gerr(umPatience, umUtility, r, k)
        relevance_ub = relevance_ub_gerr(umPatience, umUtility, target, r)
        relevance_lb = relevance_lb_gerr(umPatience, umUtility, target, r)
        difference_ub = difference_ub_gerr(umPatience, umUtility, target, r)
    if (k==1):
        disparity_lb = 0
        disparity_ub = 0
    return target, disparity_lb, disparity_ub, relevance_lb, relevance_ub, 0.0, difference_ub
#
# BOUNDS ON GROUP EXPOSURE
#
# NB. these are all quite loose bounds
#

# assume all groups get all of the exposure
def disparity_ub_rbp(p,n,k):
    e = util.gp(p,n) 
    return e * e * k

# assume all groups get equal exposure
def disparity_lb_rbp(p,n,k):
    return 0.0
    if (n == math.inf):
        return 0.0
    else:
        exposure = util.gp(p,n)
        return k * exposure * exposure

# assume the all groups get all of the exposure
def relevance_ub_rbp(p,target,n):
    attention_mass = util.gp(p,n)
    retval = 0.0
    for v in target.values():
        retval = retval + v * attention_mass
    return retval

# assume the least relevant group gets all of the exposure
def relevance_lb_rbp(p,target,n):
    return 0.0
# assume the least relevant group gets all of the exposure
def difference_ub_rbp(p,target,n):
    exposure_mass = util.gp(p,n)
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
