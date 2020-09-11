#
# function: l2
#
# returns sum_i x_i*x_i
#
def l2(x):
    if (len(x)==0):
        return float("inf")
    retval = 0.0
    for k,v in x.items():
        retval = retval + v*v
    if (retval<=0):
        return float("inf")
    return retval
#
# function: dot
#
# returns sum_i x_i * y_i
#
def dot(x,y):
    retval = 0.0
    for k,x_k in x.items():
        if k in y:
            v = x_k * y[k]
            retval = retval + v
    return retval


