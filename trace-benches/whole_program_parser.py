import csv
import re
import sys
import copy
import operator
import os.path
import numpy as np
from scipy.optimize import nnls
from scipy.linalg import solve
from sets import Set
from scipy.io import savemat

from trace import *
import pdb


high_cost = ['ARRAYLEN_GC_OP',
    'STRLEN_OP',
    'STRGETITEM_OP',
    'GETFIELD_GC_PURE_OP',
    'GETFIELD_RAW_PURE_OP',
    'GETARRAYITEM_GC_PURE_OP',
    'GETARRAYITEM_RAW_PURE_OP',
    'UNICODELEN_OP',
    'UNICODEGETITEM_OP',
    'GETARRAYITEM_GC_OP',
    'GETARRAYITEM_RAW_OP',
    'GETINTERIORFIELD_GC_OP',
    'RAW_LOAD_OP',
    'GETFIELD_GC_OP',
    'GETFIELD_RAW_OP',
    'NEW_OP',             #-> GcStruct, gcptrs inside are zeroed (not the rest)
    'NEW_WITH_VTABLE_OP',  #-> GcStruct with vtable, gcptrs inside are zeroed
    'NEW_ARRAY_OP',       #-> GcArray, not zeroed. only for arrays of primitives
    'NEW_ARRAY_CLEAR_OP', #-> GcArray, fully zeroed
    'NEWSTR_OP',           #-> STR, the hash field is zeroed
    'NEWUNICODE_OP',       #-> UNICODE, the hash field is zeroed

    'SETARRAYITEM_GC_OP',
    'SETARRAYITEM_RAW_OP',
    'SETINTERIORFIELD_GC_OP',
    'SETINTERIORFIELD_RAW_OP',    # right now, only used by tests
    'RAW_STORE_OP',
    'SETFIELD_GC_OP',
    'ZERO_PTR_FIELD_OP', # only emitted by the rewrite, clears a pointer field
                        # at a given constant offset, no descr
    'ZERO_ARRAY_OP']

loop_re = re.compile("LOOP - HASH: (?P<hash>.*) TT: (?P<tt>.*) COST: (?P<cost>.*)")
bridge_re = re.compile("BRIDGE -.*HASH: (?P<hash>.*) GUARD: *(?P<guard>\d*) COST: (?P<cost>.*)")

counts_re = re.compile("loop.*([elb]) (?P<fragment>\d*) (?P<count>\d*)") 
times_re = re.compile("\s*(\d*\.\d*) seconds time elapsed")
looptoken_re = re.compile("<Loop(\d*)>")

values = []
times = []
costs = {}
run_costs = []




#TODO: write a proper parser
for arg in sys.argv[1:]:
    print arg
    run = {}
    counts = {}
    run_times = [] 
    in_loop = False
    traces = []
    lines = []
    guards = []
    entry_points = {}
    tracing_time = 0
    backend_time = 0
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
                traces.append(build_trace(f, token=looptoken))
            elif line[0:6] == 'BRIDGE':
                in_loop = False
                tokens = line.split()
                guard = tokens[1]
                traces.append(build_trace(f, guard=guard))
            elif line[0:7] == "TRACING":
                tracing_time = 1000 *  float(line.split()[1])
                #run_times[-1] -= tracing_time
            elif line[0:7] == "BACKEND":
                backend_time =  1000 * float(line.split()[1])
                #run_times[-1] -= backend_time
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
   

    # get times from tsv file
    name = os.path.basename(arg)
    tsv_path = "CrossBenchmarks_pycket.tsv"
    average_time = 0
    with open(tsv_path, "r") as f:
        tsv = csv.reader(f, delimiter = "\t")
        #bench name starts at 15th charcater of file name
        benchname = name#[14:]
        times  = []
        for line in tsv:
            #pdb.set_trace()
            if len(line) >= 5 and line[4] == benchname and line[3] == "total":
                times.append(float(line[1]))
        average_time = sum(times)/float(len(times))
        
    
    # build fragments for each trace, flatten the list and turn it into a dic
    frags = {frag.label: frag for frag in reduce(operator.add, [trace.get_fragments(guards) for trace in traces])}
  
    eqn = {}
    for key, value in counts.iteritems():
        if value:
            if key in frags:
                frag = frags[key]
                for key2,value2 in counts.iteritems():
                    if key2 in frag.guards:
                        guard_cost = frag.cost2guard(key2)
                        value = value - value2
                        eqn[hash(frag) + 3] = value2
                        costs[hash(frag) + 3] = guard_cost
                eqn[hash(frag)] =  value
                costs[hash(frag)] = frag.cost()

    # special case for loops with no labels
    if len(frags) > len(counts):
        for key, value in frags.iteritems():
            if key in entry_points:
                count = entry_points[key]
                if count:
                    for key2,value2 in counts.iteritems():
                        if key2 in frag.guards:
                            guard_cost = frag.cost2guard(key2)
                            count = count - value2
                            eqn[hash(value) + 3] = value2
                            costs[hash(value) + 3] = guard_cost
                    eqn[hash(value)] = count
                    costs[hash(frag)] = frag.cost()
                

    with open("whole_program.dat", "w") as f:
        cost = reduce(lambda x, y: x + eqn[y] * costs[y], eqn,0)
        f.write(str(cost) + " " + str(average_time) + "\n")


    



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



