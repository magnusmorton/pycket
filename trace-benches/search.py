import argparse
import csv
import re
import operator
import numpy as np
import os.path

from scipy import stats

import trace as trace_utils


loop_re = re.compile(r"LOOP - HASH: (?P<hash>.*) TT: (?P<tt>.*) COST: (?P<cost>.*)")
bridge_re = re.compile(r"BRIDGE -.*HASH: (?P<hash>.*) GUARD: *(?P<guard>\d*) COST: (?P<cost>.*)")
counts_re = re.compile(r"loop.*([elb]) (?P<fragment>\d*) (?P<count>\d*)") 
times_re = re.compile(r"\s*(\d*\.\d*) seconds time elapsed")
looptoken_re = re.compile(r"<Loop(\d*)>")


def calculate_average_times():
    tsv_paths = ["CrossBenchmarks_pycket.tsv", "Shootout_pycket.tsv"]
    times_dict = {}
    for tsv_path in tsv_paths:
        with open(tsv_path, "r") as f:
            tsv = csv.reader(f, delimiter = "\t")
            for line in tsv:
                # line[4] is the name of the benchmark
                if len(line) >= 5 and line[3] == "total":
                    if line[4] not in times_dict:
                        times_dict[line[4]] = []
                        times_dict[line[4]].append(float(line[1]))
    return {name: sum(times)/float(len(times)) for name, times in times_dict.iteritems()}


def parse_files(filenames):
    all_traces = []
    for arg in filenames:
        print arg
        counts = {}
        run_times = [] 
        traces = []
        guards = []
        entry_points = {}
        with open(arg, 'r') as f:
            line = f.readline()
            while line:
                if line == "BEGIN":
                    # we only need the last instance of these
                    counts = {}
                    traces = []
                    guards = []
                    entry_points = {}
                m_times = times_re.match(line)
                m_counts = counts_re.match(line.rstrip())
                if line[0:4] == 'LOOP':
                    tokens = line.split()
                    looptoken = int(looptoken_re.match(tokens[1]).group(1))
                    traces.append(trace_utils.build_trace(f, token=looptoken))
                elif line[0:6] == 'BRIDGE':
                    tokens = line.split()
                    guard = tokens[1]
                    traces.append(trace_utils.build_trace(f, guard=guard))
                if m_times:
                    run_times.append(float(m_times.group(1)))
                if m_counts:
                    count = float(m_counts.group("count"))
                    if count > 0:
                        if m_counts.group(1) == 'e':
                            entry_points[int(m_counts.group("fragment"))] = count
                        counts[int(m_counts.group("fragment"))] = count
                        if m_counts.group(1) == 'b':
                            guards.append(int(m_counts.group("fragment")))
                line = f.readline()


        # build fragments for each trace, flatten the list and turn it into a dic
        frags = {frag.label: frag for frag in reduce(operator.add, [trace.get_fragments(guards) for trace in traces])}
        name = os.path.basename(arg)
        all_traces.append(trace_utils.Program(name, frags, counts, entry_points))
    return all_traces


def fit(costs, times):
    # import pdb
    # pdb.set_trace()
    x = np.array(costs)
    y = np.array(times)
    _,_,r,_,_ = stats.linregress(x,y)
    return r**2

def combinations_with_replacement(iterable, r, start=None):
    # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC                                                                                   
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    if start is None:
        indices = [0] * r
    else:
        assert len(start) == r
        indices = [pool.index(l) for l in start]
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)
        

def main():
    parser = argparse.ArgumentParser(description="Run cost analysis")
    parser.add_argument("filenames", metavar="<file>", nargs = '+')
    parser.add_argument("--start", "-s",  default="0,0,0,0,0")
    parser.add_argument("--cap", "-c", default="10")


    args = parser.parse_args()
    start = [int(num) for num in args.start.split(",")]
    average_times = calculate_average_times()
    programs = parse_files(args.filenames)

    best = None
    print "Beginning search...."
    for model in combinations_with_replacement(range(int(args.cap) + 1), 5, start):
        print "current model:", model
        trace_utils.Fragment.model = model
        costs = [program.cost() for program in programs]
        times = [average_times[program.name] for program in programs]
        rsq = fit(costs, times)
        print "rsq", rsq
        if not best:
            best = (model, rsq)
        elif rsq < best[1]:
            best = (model, rsq)
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



