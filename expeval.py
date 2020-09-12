#!/usr/bin/env python3

import argparse
import math
import metrics
import data
import individual
import group
import util
#
# 
#


def main():
    parser = argparse.ArgumentParser(description='exposure evaluation')
    parser.add_argument('-I', dest='topfn')
    parser.add_argument('-R', dest='relfn')
    parser.add_argument('-u', dest='umType', default="gerr")
    parser.add_argument('-p', dest='umPatience', default=0.50)
    parser.add_argument('-r', dest='umUtility', default=0.50)
    parser.add_argument('-b', dest='binarize', default=False)
    parser.add_argument('-g', dest='group', default=False, action='store_true')
    parser.add_argument('-c', dest='complete', default=False, action='store_true')

    args = parser.parse_args()

    umType = args.umType
    umPatience=float(args.umPatience)
    umUtility=float(args.umUtility)
    binarize = bool(args.binarize)
    groupEvaluation = bool(args.group)
    complete = bool(args.complete)
    #
    # get target exposures
    #
    qrels, did2gids = data.read_qrels(args.relfn, binarize, complete)
    targetExposures = {}
    disparity_lb = {}
    disparity_ub = {}
    relevance_lb = {}
    relevance_ub = {}
    difference_ub = {}
    for qid, qrels_qid in qrels.items():
        target, disp_lb, disp_ub, rel_lb, rel_ub, diff_lb, diff_ub = individual.target_exposures(qrels_qid, umType, umPatience, umUtility, complete)
        targetExposures[qid] = target
        disparity_lb[qid] = disp_lb
        disparity_ub[qid] = disp_ub
        relevance_lb[qid] = rel_lb
        relevance_ub[qid] = rel_ub
        difference_ub[qid] = diff_ub
        
    group_targetExposures = {}
    group_disparity_lb = {}
    group_disparity_ub = {}
    group_relevance_lb = {}
    group_relevance_ub = {}
    group_difference_ub = {}
    
    if groupEvaluation:
        for qid, targetExposures_qid in targetExposures.items():
             target, disp_lb, disp_ub, rel_lb, rel_ub, diff_lb, diff_ub = group.target_exposures(targetExposures_qid, did2gids[qid], qrels[qid], umType, umPatience, umUtility, complete)
             group_targetExposures[qid] = target
             group_disparity_lb[qid] = disp_lb
             group_disparity_ub[qid] = disp_ub
             group_relevance_lb[qid] = rel_lb
             group_relevance_ub[qid] = rel_ub
             group_difference_ub[qid] = diff_ub
             
    #
    # get treatment exposures
    #
    rls = data.read_topfile(args.topfn)
    treatmentExposures = {}
    for qid, rls_qid in rls.items():
        if (qid in qrels):
            treatmentExposures[qid] = individual.treatment_exposures(rls_qid, qrels[qid], umType, umPatience, umUtility)
    group_treatmentExposures = {}
    if groupEvaluation:
        for qid, treatmentExposures_qid in treatmentExposures.items():
            if (qid in did2gids):
                group_treatmentExposures[qid] = group.treatment_exposures(treatmentExposures_qid, did2gids[qid], qrels[qid])
    
    #
    # compute exposure metrics
    #    
    for qid in targetExposures.keys():
        disparity_qid = 0
        relevance_qid = 0
        if groupEvaluation:
            if (len(group_treatmentExposures[qid])>0):
                disp_lb = group_disparity_lb[qid]
                disp_ub = group_disparity_ub[qid]
                if (disp_lb == disp_ub):
                    disparity_qid = 0.0
                else:
                    disparity_qid = metrics.disparity(group_targetExposures[qid], group_treatmentExposures[qid])
                    disparity_qid = (disparity_qid - disp_lb) / (disp_ub - disp_lb)
                
                rel_ub = group_relevance_ub[qid]
                rel_lb = group_relevance_lb[qid] 
                if (rel_ub == rel_lb):
                    relevance_qid = 1.0
                else:                               
                    relevance_qid = metrics.relevance(group_targetExposures[qid], group_treatmentExposures[qid])
                    relevance_qid = (relevance_qid - rel_lb) / (rel_ub - rel_lb)
                
                
                diff_ub = group_difference_ub[qid]            
                difference_qid = metrics.ee(group_targetExposures[qid], group_treatmentExposures[qid])
                difference_qid = difference_qid / diff_ub
                                
                print("\t".join(["disparity",qid,"%f"%disparity_qid]))
                print("\t".join(["relevance",qid,"%f"%relevance_qid]))
                print("\t".join(["difference",qid,"%f"%difference_qid]))
        else:
            disp_lb = disparity_lb[qid]
            disp_ub = disparity_ub[qid]
            disparity_qid = metrics.disparity(targetExposures[qid], treatmentExposures[qid])
            disparity_qid = (disparity_qid - disp_lb) / (disp_ub - disp_lb)
            
            rel_ub = relevance_ub[qid]
            rel_lb = relevance_lb[qid]
            if (rel_ub == rel_lb):
                relevance_qid = 1.0
            else:
                relevance_qid = metrics.relevance(targetExposures[qid], treatmentExposures[qid])
                relevance_qid = (relevance_qid - rel_lb) / (rel_ub - rel_lb)
            
            diff_ub = difference_ub[qid]
            difference_qid = metrics.ee(targetExposures[qid], treatmentExposures[qid])
            difference_qid = difference_qid / diff_ub
            
            print("\t".join(["disparity",qid,"%f"%disparity_qid]))
            print("\t".join(["relevance",qid,"%f"%relevance_qid]))
            print("\t".join(["difference",qid,"%f"%difference_qid]))
        

if __name__ == '__main__':
    main()
