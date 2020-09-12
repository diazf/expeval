import util
import math
def target_exposures(qrels, umType, umPatience, umUtility, complete):
    #
    # compute [ [relevanceLevel, count], ...] vector
    #
    relevanceLevels = []
    for did,rel in qrels.items():
        found = False
        for i in range(len(relevanceLevels)):
            if (relevanceLevels[i][0] == rel):
                relevanceLevels[i][1] = relevanceLevels[i][1] + 1
                found = True
                break
        if (not found):
            r = [rel,1]
            relevanceLevels.append(r)
    relevanceLevels.sort(reverse=True)
    # if len(relevanceLevels)<=1:
    #     return None, -1, -1, -1, -1, -1, -1
    #
    # compute { relevanceLevel : exposure }
    #
    numDominating = 0
    targetExposurePerRelevanceLevel = {}
    for i in range(len(relevanceLevels)):
        grade = relevanceLevels[i][0]
        m = relevanceLevels[i][1]
        if (umType == "rbp"):
            targetExposurePerRelevanceLevel[grade] = (pow(umPatience,numDominating) - pow(umPatience,numDominating+m)) / (m*(1.0-umPatience))
        elif (umType == "gerr"):
            umModulatedPatience = umPatience * (1.0 - umUtility)
            targetExposurePerRelevanceLevel[grade] = (pow(umModulatedPatience,numDominating) - pow(umModulatedPatience,numDominating+m)) / (m*(1.0-umModulatedPatience))
        numDominating = numDominating + m
    #
    # create { did : exposure }
    #
    target = {}
    for did,rel in qrels.items():
        target[did] = targetExposurePerRelevanceLevel[rel]
    


    n = len(qrels) if (complete) else math.inf
    disparity_lb = 0.0
    disparity_ub = 0.0
    relevance_lb = 0.0
    relevance_ub = 0.0
    difference_lb = 0.0
    difference_ub = 0.0
    
    if (umType == "rbp"):
        disparity_ub = disparity_ub_rbp(umPatience, n)
        disparity_lb = disparity_lb_rbp(umPatience, n)
        relevance_ub = util.l2(target)
        relevance_lb = relevance_lb_rbp(target,umPatience, n)
        difference_ub = difference_ub_rbp(umPatience, target, n)
    elif (umType == "gerr"):
        disparity_ub = disparity_ub_gerr(umPatience, umUtility, relevanceLevels, n)
        disparity_lb = disparity_lb_gerr(umPatience, umUtility, relevanceLevels, n)
        relevance_ub = util.l2(target)
        relevance_lb = relevance_lb_gerr(umPatience, umUtility, target, n)
        difference_ub = difference_ub_gerr(umPatience, umUtility, target, n)
    if len(relevanceLevels) <= 1:
        relevance_lb = 0
        relevance_ub = 0
    return target, disparity_lb, disparity_ub, relevance_lb, relevance_ub, 0.0, difference_ub

def treatment_exposures(rls, qrels, umType, umPatience, umUtility):
    numSamples = len(rls.keys())
    exposures = {}
    for itr,rl in rls.items():
        rl.sort(reverse=True)
        relret = 0
        for i in range(len(rl)):
            did = rl[i][1]
            if not(did in exposures):
                exposures[did] = 0.0
            if (umType == "rbp"):
                exposures[did] = exposures[did] + umPatience**(i) / numSamples
            elif (umType == "gerr"):
                exposures[did] = exposures[did] + (umPatience**(i) * (1.0-umUtility)**(relret)) / numSamples
            if did in qrels:
                relret = relret + 1
    return exposures
    

#
# BOUNDS ON INDIVIDUAL EXPOSURE
#

# ( 1-p^(2n) ) / ( 1-p^2 )
def disparity_ub_rbp(p,n):
    return util.gp(p*p,n)

# ( ( 1-p^n ) / ( 1-p ) )^2 / k
def disparity_lb_rbp(p,n):
    if (n == math.inf):
        return 0.0
    else:
        return pow( util.gp(p,n), 2 ) / n

def difference_ub_rbp(p,target,n):
    retval = 0.0
    if (n == math.inf):
        for d,e in target.items():
            retval = retval + e*e
        retval = retval + (1.0 / ( 1.0 - (p*p) ))
    else:
        dist = []
        for d,e in target.items():
            dist.append(e)
        dist.sort()
        for i in range(len(dist)):
            diff = pow(p,i) - dist[i]
            retval = retval + diff*diff
    return retval
def relevance_lb_rbp(p,target,n):
    retval = 0.0
    if (n != math.inf):
        dist = []
        for d,e in target.items():
            dist.append(e)
        dist.sort()
        # print(dist)
        for i in range(len(dist)):
            retval = retval + pow(p,i)*dist[i]
        # print(retval)
    return retval

# loose upper bound: assume that no documents are relevant = rbp(p,n)
def disparity_ub_gerr(p,u,r,n):
    return disparity_ub_rbp(p,n)
    

# loose lower bound: assume that all documents are relevant = rbp(u*p,n)
def disparity_lb_gerr(p,u,r,n):
    return disparity_lb_rbp(p*u,n)

def relevance_lb_gerr(p,u,target,n):
    return relevance_lb_rbp(p*u,target,n)

def difference_ub_gerr(p,u,target,n):
    retval = 0.0
    if (n == math.inf):
        for d,e in target.items():
            retval = retval + e*e
        retval = retval + (1.0 / ( 1.0 - (p*p) ))
    else:
        dist = []
        for d,e in target.items():
            dist.append(e)
        dist.sort()
        for i in range(len(dist)):
            diff = pow(p*u,i) - dist[i]
            retval = retval + diff*diff
    return retval
