#!/usr/bin/env python3

import argparse
import json
import csv

def main():
    parser = argparse.ArgumentParser(description='convert fair ranking runfile json to trec runfile')
    parser.add_argument('-I', dest='runfile')

    args = parser.parse_args()

    runfile = args.runfile
    qid_cnts = {}
    with open(runfile,"r") as fp:
        for line in fp:
            data = json.loads(line.strip())
            qid = "%d"%data["qid"]
            if not (qid in qid_cnts):
                qid_cnts[qid] = 0
            else:
                qid_cnts[qid] = qid_cnts[qid] + 1
            qid_idx = qid_cnts[qid]
            rank = 1
            for did in data["ranking"]:                
                print("%s\tQ%d\t%s\t%d\t%f"%(qid, qid_idx, did, rank, 1.0/rank))
                rank = rank + 1
        
if __name__ == '__main__':
    main()
