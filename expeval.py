#!/usr/bin/env python3

import metrics
import data
import individual
import group
import util
import cli
import sys
#
# 
#
def main():
    parameters = cli.parseArguments()

    umType = parameters["umType"]
    umPatience = parameters["umPatience"]
    umUtility = parameters["umUtility"]
    binarize = parameters["binarize"]
    groupEvaluation = parameters["groupEvaluation"]
    complete = parameters["complete"]
    normalize = parameters["normalize"]    
    relfn = parameters["relfn"]
    topfn = parameters["topfn"]
    #
    # get target exposures
    #
    qrels, did2gids = data.read_qrels(relfn, binarize, complete)
    targExp = {}
    disparity  = {}
    relevance  = {}
    difference = {}
    for qid, qrels_qid in qrels.items():
        targ, disp, rel, diff = individual.target_exposures(qrels_qid, 
                                                            umType, umPatience,
                                                            umUtility, complete)
        targExp[qid] = targ
        disparity[qid] = disp
        relevance[qid] = rel
        difference[qid] = diff
        
    #
    # aggregate exposures if group evaluation and replace queries missing groups 
    # with nulls
    #
    if groupEvaluation:
        for qid in targExp.keys():
            if qid in did2gids:
                t = targExp[qid]
                targ, disp, rel, diff = group.target_exposures(t, did2gids[qid], 
                                                               qrels[qid], umType, 
                                                               umPatience, umUtility, 
                                                               complete)
                targExp[qid] = targ
                disparity[qid] = disp
                relevance[qid] = rel
                difference[qid] = diff
            else:
                targExp[qid] = None
                disparity[qid] = None
                relevance[qid] = None
                difference[qid] = None
             
    #
    # get treatment exposures
    #
    permutations = data.read_topfile(topfn)
    runExp = {}
    for qid, permutations_qid in permutations.items():
        if (qid in qrels):
            runExp[qid] = individual.treatment_exposures(permutations_qid, qrels[qid], 
                                                         umType, umPatience,   
                                                         umUtility)
    #
    # aggregate exposures if group evaluation and replace queries missing groups 
    # with nulls
    #
    if groupEvaluation:
        for qid in runExp.keys():
            if (qid in did2gids):
                r = runExp[qid]
                runExp[qid] = group.treatment_exposures(r, did2gids[qid], qrels[qid])
            else:
                runExp[qid] = None
    #
    # compute and print per-query individual metrics
    #
    for qid in targExp.keys():
        #
        # skip queries with null targets.  this happens if there is an
        # upstream problem (e.g. no relevant documents or no groups)
        #
        if (targExp[qid] == None):
            continue
        if (not(qid in runExp)) or (len(runExp[qid]) == 0):
            #
            # defaults for queries in relfn and not in topfn
            #
            disparity[qid].value = disparity[qid].upperBound
            relevance[qid].value = relevance[qid].lowerBound  
            difference[qid].value = relevance[qid].upperBound             
        else:
            #
            # compute the metrics for queries with results
            #
            t = targExp[qid]
            r = runExp[qid]
            disparity[qid].value = metrics.disparity(t,r)
            relevance[qid].value = metrics.relevance(t,r)            
            difference[qid].value = metrics.ee(t,r)
        #
        # output
        #
        print("\t".join([disparity[qid].name, qid, str(disparity[qid].get(normalize))]))
        print("\t".join([relevance[qid].name, qid, str(relevance[qid].get(normalize))]))
        print("\t".join([difference[qid].name, qid, str(difference[qid].get(normalize))]))
        

if __name__ == '__main__':
    main()
