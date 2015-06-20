import argparse
import numpy as np
import time
import signal
import sys
from itertools import izip

from scipy import stats

import trace as trace_utils
import trace_parser




def half_add(a, b, cap):
    s = a + b
    r = s - cap
    c = 0
    if r >= 0:
        c = 1
        s = r
    return (s, c)

def full_add(a, b, cap, step):
    pairs = zip(a,b)
    pairs.reverse()
    result = []
    carry = 0
    for pair in pairs:
        res = half_add(pair[0], pair[1] + carry, cap)
        result.append(res[0])
        carry = res[1] * step
    result.reverse()
    return result
        

def models(start, end, cap, step):
    current = list(start)
    while current != end:
        current = full_add(current, step, cap, step[-1])
        yield current

        
def fit(costs, times):
    # import pdb
    # pdb.set_trace()
    x = np.array(costs)
    y = np.array(times)
    _,_,r,_,_ = stats.linregress(x,y)
    return r**2

def main():
    parser = argparse.ArgumentParser(description="Run cost analysis")
    parser.add_argument("filenames", metavar="<file>", nargs = '+')
    parser.add_argument("--start", "-s",  default="0,0,0,0,0")
    parser.add_argument("--end", "-e",  default="1,0,0,0,0")
    parser.add_argument("--cap", "-c", default=11, type=int)
    parser.add_argument("--step", "-t", default=1, type=int)
    
    args = parser.parse_args()
    start = [int(num) for num in args.start.split(",")]
    end = [int(num) for num in args.end.split(",")]
    step = [0,0,0,0,args.step]
    average_times = trace_parser.calculate_average_times()
    programs = trace_parser.parse_files(args.filenames)
    counts = {program.name: program.class_counts() for program in programs}
    dot = lambda x,y: sum(a*b for a,b in izip(x,y))
    best = None
    def handler(s, frame):
        print "Terminated... Current best:", best
        sys.exit(0)
    signal.signal(signal.SIGINT, handler)
    print "Beginning search...."
    then = time.clock()
    for model in models(start,end,args.cap, step):
        trace_utils.Fragment.model = model
        costs = [dot(counts[program.name], model) for program in programs]
        times = [average_times[program.name] for program in programs]
        rsq = fit(costs, times)
        if not best:
            best = (model, rsq)
        elif rsq > best[1]:
            best = (model, rsq)
    now = time.clock()

    print "Time:", now - then
    print "Best:", best


if __name__ == '__main__':
    main()

    



# max_len = 0
# longest = None
# for val in values:
#     if len(val) > max_len:
#         max_len = len(val)
#         longest = val

# zero_longest = {key:0 for key in longest}
# values = [dict(zero_longest.items() + val.items()) for val in values]

# # need values in key order
# coeffs = [[value for (key, value) in sorted(eqn.items())] for eqn in values]    

# a = np.array(coeffs)
# b = np.array(times)



# savemat("results.mat", {"counts":a, "times":b})
# # we are probably overconstrained
# x = nnls(a, b)
                
# sorted_costs = [value for (key, value) in sorted(costs.items())]



