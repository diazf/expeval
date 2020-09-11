def target_exposures(qrels, umType, umPatience, umUtility):
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
    return target

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
def group_exposure(exposures, did2gids):
    retval = {}
    for did,gids in did2gids.items():
        for gid in gids:
            if not(gid in retval):
                retval[gid] = 0.0
            if did in exposures:
                retval[gid] = retval[gid] + exposures[did]
    return retval
