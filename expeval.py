#!/usr/bin/env python3

import argparse
import math
import metrics
import data
import exposure
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

    args = parser.parse_args()

    umType = args.umType
    umPatience=float(args.umPatience)
    umUtility=float(args.umUtility)
    binarize = bool(args.binarize)
    group = bool(args.group)
    #
    # get target exposures
    #
    qrels, did2gids = data.read_qrels(args.relfn, binarize)
    targetExposures = {}
    for qid, qrels_qid in qrels.items():
        targetExposures[qid] = exposure.target_exposures(qrels_qid, umType, umPatience, umUtility)
    targetGroupExposures = {}
    if group:
        for qid, targetExposures_qid in targetExposures.items():
            targetGroupExposures[qid] = exposure.group_exposure(targetExposures_qid, did2gids[qid])
    #
    # get treatment exposures
    #
    rls = data.read_topfile(args.topfn)
    treatmentExposures = {}
    for qid, rls_qid in rls.items():
        if (qid in qrels):
            treatmentExposures[qid] = exposure.treatment_exposures(rls_qid, qrels[qid], umType, umPatience, umUtility)
    treatmentGroupExposures = {}
    if group:
        for qid, treatmentExposures_qid in treatmentExposures.items():
            if (qid in did2gids):
                treatmentGroupExposures[qid] = exposure.group_exposure(treatmentExposures_qid, did2gids[qid])
    
    #
    # compute exposure metrics
    #    
    for qid in targetExposures.keys():
        disparity_qid = 0
        relevance_qid = 0
        if group:
            if (len(treatmentGroupExposures[qid])>0):
                disparity_qid = metrics.disparity(targetGroupExposures[qid], treatmentGroupExposures[qid])
                relevance_qid = metrics.relevance(targetGroupExposures[qid], treatmentGroupExposures[qid])
                ee_qid = metrics.ee(targetGroupExposures[qid], treatmentGroupExposures[qid])
                print("\t".join(["disparity",qid,"%f"%disparity_qid]))
                print("\t".join(["relevance",qid,"%f"%relevance_qid]))
                print("\t".join(["ee",qid,"%f"%ee_qid]))
        else:
            disparity_qid = metrics.disparity(targetExposures[qid], treatmentExposures[qid])
            relevance_qid = metrics.relevance(targetExposures[qid], treatmentExposures[qid])
            ee_qid = metrics.ee(targetExposures[qid], treatmentExposures[qid])
            print("\t".join(["disparity",qid,"%f"%disparity_qid]))
            print("\t".join(["relevance",qid,"%f"%relevance_qid]))
            print("\t".join(["ee",qid,"%f"%ee_qid]))
        

if __name__ == '__main__':
    main()
