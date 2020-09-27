import util
import math
import permutation
from metrics import Metric
#
# function: target_exposures
#
# given a user model and its paramters, compute the target exposures for 
# documents.

#
def target_exposures(qrels, umType, umPatience, umUtility, complete):
    #
    # compute [ [relevanceLevel, count], ...] vector
    #
    relevanceLevelAccumulators = {}
    relevanceLevels = []
    for did,rel in qrels.items():
        if rel in relevanceLevelAccumulators:
            relevanceLevelAccumulators[rel] = relevanceLevelAccumulators[rel] + 1
        else:
            relevanceLevelAccumulators[rel] = 1
    for k,v in relevanceLevelAccumulators.items():
        relevanceLevels.append([k,v])
    relevanceLevels.sort(reverse=True)
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
    disparity = Metric("disparity", 0.0)
    relevance = Metric("relevance", 1.0)
    difference = Metric("difference", 0.0)
    
    if (umType == "rbp"):
        disparity.upperBound = disparity_ub_rbp(umPatience, n)
        disparity.lowerBound = disparity_lb_rbp(umPatience, n)
        relevance.upperBound = util.l2(target, False)
        relevance.lowerBound = relevance_lb_rbp(target,umPatience, n)
        difference.upperBound = difference_ub_rbp(umPatience, target, n)
        difference.lowerBound = 0.0
    elif (umType == "gerr"):
        disparity.upperBound = disparity_ub_gerr(umPatience, umUtility, relevanceLevels, n)
        disparity.lowerBound = disparity_lb_gerr(umPatience, umUtility, relevanceLevels, n)
        
        relevance.upperBound = util.l2(target, False)
        relevance.lowerBound = relevance_lb_gerr(umPatience, umUtility, target, n)
        
        difference.upperBound = difference_ub_gerr(umPatience, umUtility, target, n)
        difference.lowerBound = 0.0
    if len(relevanceLevels) <= 1:
        relevance.lowerBound = 0.0
        relevance.upperBound = 0.0
    return target, disparity, relevance, difference

def treatment_exposures(permutations, qrels, umType, umPatience, umUtility):
    numSamples = len(permutations.keys())
    exposures = {}
    for itr,permutation in permutations.items():
        p = permutation.value()
        relret = 0
        for i in range(len(p)):
            did = p[i]
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
    return util.geometricSeries(p*p,n)

# ( ( 1-p^n ) / ( 1-p ) )^2 / k
def disparity_lb_rbp(p,n):
    if (n == math.inf):
        return 0.0
    else:
        return pow( util.geometricSeries(p,n), 2 ) / n

#
# function: difference_ub_rbp
#
# retrieval setting (n == math.inf)
#
# assume that all of the documents in target exposure with values > 0 are at 
# the bottom of the ranking.  the upper bound, then, is decomposed into two 
# parts.  we assume that the exposure at the end of the ranking is effectively
# zero and the quantity is the exposure "lost" from the relevant documents,
#
# \sum_{i=0}^{len(target)} target(i)*target(i)
#
# and the second is the exposure "gained" for the nonrelevant documents.  we 
# assume that the corpus is of infinite size and that the relevant documents
# are all at the end.  we're technically double counting the end but the
# contribution to the geometric series is so small it should not matter.  
#
# \sum_{i=0} p^i * p^i 
#
# reranking setting (n != math.inf)
#
# assume the worst exposure is a static ranking in reverse order of relevance
#
def difference_ub_rbp(p,target,n):
    ub = 0.0
    if (n == math.inf):
        #
        # retrieval condition
        #
        
        # contribution lost from relevant documents
        for d,e in target.items():
            ub = ub + e*e
        # contribution gained from nonrelevant documents
        ub = ub + util.geometricSeries(p,n)
    else:
        #
        # reranking condition
        #
        # construct the sorted target exposure
        target_vector = []
        for d,e in target.items():
            target_vector.append(e)
        target_vector.sort()
        for i in range(len(target_vector)):
            diff = pow(p,i) - target_vector[i]
            ub = ub + diff*diff
    return ub
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
    return difference_ub_rbp(p,target,n)

