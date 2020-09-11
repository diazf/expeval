#
# read_qrels
#
# QID GID DID REL
#

def read_qrels(fn, binarize):
    qrels={}
    did2gids = {}
    #
    # read qrels
    #
    fp = open(fn,"r")
    for line in fp:
        fields = line.strip().split()
        if (len(fields) == 3):
            qid = fields[0]
            itr = "-1"
            did = fields[1]
            rel = fields[2]
        else:
            qid = fields[0]
            itr = fields[1]
            did = fields[2]
            rel = fields[3]
        gids = []
        gids = map(lambda x: int(x), itr.split("|"))
            
        rel=int(rel)
        if (rel>0):
            if (binarize):
                rel = 1
            if not(qid in qrels):
                qrels[qid] = {}
                did2gids[qid] = {}
            qrels[qid][did] = rel
            if not(did in did2gids[qid]):
                did2gids[qid][did] = []
            for gid in gids:
                if not (gid in did2gids[qid][did]):
                    did2gids[qid][did].append(gid)
    fp.close()
    return qrels, did2gids

    

def read_topfile(fn):
    #
    # get ranked lists
    #
    fp = open(fn,"r")
    sample_ids=set([])
    rls = {} # qid, iteration ,[score,did]
    for line in fp:
        fields = line.strip().split()
        qid,itr,did,rank,score=fields[:5]
        sample_ids.add(itr)
        score = float(score)
        rank = int(rank)
        if not(qid in rls):
            rls[qid] = {}
        if not(itr in rls[qid]):
            rls[qid][itr] = []
        rls[qid][itr].append([score,did])
    fp.close()
    return rls
