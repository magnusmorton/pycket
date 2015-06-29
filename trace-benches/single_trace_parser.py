import re
import sys
import copy
import operator
import numpy as np
import instructions
import trace
from scipy.optimize import nnls
from scipy.linalg import solve
from sets import Set
from scipy.io import savemat
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
target_token_re = re.compile(".*TargetToken\((?P<tt_val>\d*)\)")
counts_re = re.compile("loop.*([elb]) (?P<fragment>\d*) (?P<count>\d*)") 
times_re = re.compile("cpu time: (\d*) real time: \d* gc time: \d*")
looptoken_re = re.compile("<Loop(\d*)>")



def null_cost(frag, i=None):
    return 1

def simple_cost(frag, i=None):
    return len(filter( lambda x: x.split()[0] != "DEBUG_MERGE_POINT_OP",frag.ops[0:None]))

def mem_cost(frag, i=None):
    if not i:
        i = len(frag.ops)
    j = 0
    cost = 0
    while j < i:
        op = frag.ops[j].split()[0]
        if op in high_cost:
            cost += 1000
        elif op != "DEBUG_MERGE_POINT_OP":
            cost += 1
        j+=1
    return cost

def weighted_costs(self, i=None):
    if not i:
        i = len(self.ops)
    j = 0
    counts = [0]*5
    while j < i:
        op = self.ops[j].split()[0]
        if op in instructions.object_ops:
            counts[0] += 267
        elif op in instructions.array_ops:
            counts[1] += 0
        elif op in instructions.num_ops:
            counts[2] += 1387
        elif op in instructions.alloc_ops:
            counts[3] += 9494
        elif op == "GUARD:":
            counts[4] += 0
        j += 1
    return counts

class Trace(object):
    def __init__(self, ops, token=None):
        self.ops = ops
        self.token = token

    def __eq__(self, other):
        return hash(self) == hash(other)

    def get_fragments(self, guards, current_label=None):
        fragments = []
        start_pos = 0
        found_guards = {}
        for i, op in enumerate(self.ops):
            tokens  = op.split()
            if tokens[0] == "LABEL:":
                if current_label:
                    fragments.append(Fragment(self.ops[start_pos:i], current_label, found_guards))
                current_label = int(target_token_re.match(tokens[1]).group('tt_val'))
                start_pos = i
                found_guards = {}
                print "LABEL:", current_label
            if tokens[0] == "JUMP_OP":
                if current_label:
                    fragments.append(Fragment(self.ops[start_pos:], current_label, found_guards))
                else:
                    fragments.append(Fragment(self.ops,self.token, found_guards))
            if tokens[0] == "GUARD:":
                guard = int(tokens[1])
                if guard in guards:
                    # store the index of the guard from the start of the trace
                    found_guards[guard] = i - start_pos
        return fragments
                

class Bridge(Trace):
    def __init__(self, ops, guard):
        super(Bridge, self).__init__(ops)
        self.guard = guard

    def get_fragments(self, guards):
        # just use the bridge's guard id as a label
        return super(Bridge, self).get_fragments(guards, self.guard)

class Fragment(object):
    cost_fn = null_cost
    def __init__(self, ops, label, guards):
        self.ops = ops
        self.label = label
        self.guards = guards


    def cost(self):
        return Fragment.cost_fn(self)
    
    def cost2guard(self, guard):
#        return len(filter( lambda x: x != "DEBUG_MERGE_POINT_OP",self.ops[0:self.guards[guard]]))
        return Fragment.cost_fn(self, self.guards[guard])
            

    def __hash__(self):
        hash_num = 0
        for op in self.ops:
            hash_num *= 251
            hash_num += hash(op.split()[0])
        return hash_num

def build_trace(fd, guard=0, token=None):
    ops = []
    line = fd.readline().rstrip()
    trace = None
    while line and line != "END TRACE":
        ops.append(line.lstrip('<').rstrip('>'))
        line = fd.readline().rstrip()
    if guard > 0:
        trace = Bridge(ops, guard)
    else:
        trace = Trace(ops, token)
    return trace


#TODO: write a proper parser
for arg in sys.argv[1:]:
    run = {}
    counts = {}
    run_times = [] 
    in_loop = False
    traces = []
    lines = []
    guards = []
    this_times = []
    entry_points = {}
    tracing_time = 0
    backend_time = 0
    values = []
    times = []
    costs = {}
    run_costs = []

    with open(arg, 'r') as f:
        line = f.readline()
        while line:
            if line[0:-1] == "BEGIN":
                counts = {}
                traces = []
                guards = []
                entry_points = {}
                this_times = []
            m_times = times_re.match(line.rstrip())
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
                print "TIME", m_times.group(1)
            if m_counts:
                count = float(m_counts.group("count"))
                if count > 0:
                    if m_counts.group(1) == 'e':
                        entry_points[int(m_counts.group("fragment"))] = count
                    counts[int(m_counts.group("fragment"))] = count
                    if m_counts.group(1) == 'b':
                        guards.append(int(m_counts.group("fragment")))
            line = f.readline()
    
    print "AVG TIME", sum(run_times) / len(run_times)
    # build fragments for each trace, flatten the list and turn it into a dic
    frags = {frag.label: frag for frag in reduce(operator.add, [trace.get_fragments(guards) for trace in traces])}
    # bad idea
    last_frag = None
    last_count = 0 
    for key, value in counts.iteritems():
        if key in frags:
            frag = frags[key]
            last_frag = frag
            last_count = value
            for key2,value2 in counts.iteritems():
                if key2 in frag.guards:
                    guard_cost = frag.cost2guard(key2)
                    value = value - (value2 + 200)
                    print "Fragment:", key2, "Cost:", guard_cost, "Count:", value2
            print "Fragment:", key, "Cost:", frag.cost(), "Count:", value

    with open("gennew_results.plt", "a") as f:
        f.write( str((sum(run_times) / len(run_times)) / (last_count + 131)) + " " + str(last_frag.cost()) + "\n" )
