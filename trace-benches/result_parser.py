import re
import sys
import operator
import numpy as np
import numpy.linalg as linalg
from sets import Set
import pdb

loop_re = re.compile("LOOP - HASH: (?P<hash>.*) TT: (?P<tt>.*) COST: (?P<cost>.*)")
bridge_re = re.compile("BRIDGE -.*HASH: (?P<hash>.*) GUARD: *(?P<guard>\d*) COST: (?P<cost>.*)")
target_token_re = re.compile(".*TargetToken\((?P<tt_val>\d*)\)")
counts_re = re.compile("loop.*([lb]) (?P<fragment>\d*) (?P<count>\d*)") 
times_re = re.compile("cpu time: (\d*) real time: \d* gc time: \d*")
values = []
times = []
costs = {}

class Trace(object):
    def __init__(self, ops):
        self.ops = ops

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
            if tokens[0] == "JUMP_OP":
                if current_label:
                    fragments.append(Fragment(self.ops[start_pos:], current_label, found_guards))
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
    def __init__(self, ops, label, guards):
        self.ops = ops
        self.label = label
        self.guards = guards


    def cost(self):
        return len(filter( lambda x: x != "DEBUG_MERGE_POINT_OP",self.ops))
    
    def cost2guard(self, guard):
        """
        """
        return len(filter( lambda x: x != "DEBUG_MERGE_POINT_OP",self.ops[0:self.guards[guard]]))
            

    def __hash__(self):
        hash_num = 0
        for op in self.ops:
            hash_num *= 251
            hash_num += hash(op.split()[0])
        return hash_num

def build_trace(fd, guard=0):
    ops = []
    line = fd.readline().rstrip()
    trace = None
    while line and line != "END TRACE":
        ops.append(line.lstrip('<').rstrip('>'))
        line = fd.readline().rstrip()
    if guard > 0:
        trace = Bridge(ops, guard)
    else:
        trace = Trace(ops)
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
    with open(arg, 'r') as f:
        line = f.readline().rstrip()
        while line:
            if line == "BEGIN":
                # we only need the last instance of these
                counts = {}
                traces = []
                guards = []
            m_times = times_re.match(line)
            m_counts = counts_re.match(line)
            if line[0:4] == 'LOOP':
                traces.append(build_trace(f))
            elif line[0:6] == 'BRIDGE':
                in_loop = False
                tokens = line.split()
                guard = tokens[1]
                traces.append(build_trace(f, guard))
            if m_times:
                run_times.append(int(m_times.group(1)))
            if m_counts:
                counts[int(m_counts.group("fragment"))] = int(m_counts.group("count"))
                if m_counts.group(1) == 'b':
                    guards.append(int(m_counts.group("fragment")))
            line = f.readline().rstrip()
   
    
    # build fragments for each trace, flatten the list and turn it into a dic
    frags = {frag.label: frag for frag in reduce(operator.add, [trace.get_fragments(guards) for trace in traces])}
  
    eqn = {}
    for key, value in counts.iteritems():
        # TODO: count bridge labels
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
    times.append(reduce(lambda x, y: x+y, run_times) / float(len(run_times)))
    values.append(eqn)


# need max length
max_len = 0
for val in values:
    if len(val) > max_len:
        max_len = len(val)

# need ordered keys
pdb.set_trace()
coeffs = []
for eqn in values:
    sorted_eqn = [value for (key, value) in sorted(eqn.items())]
    #pad with 0s
    sorted_eqn.extend([0]* (max_len - len(sorted_eqn)))
    coeffs.append(sorted_eqn)
    

a = np.array(coeffs)
b = np.array(times)


# we are probably overconstrained
x = linalg.lstsq(a, b, 0)


sorted_costs = [value for (key, value) in sorted(costs.items())]
                
for i, cost in enumerate(sorted_costs):
    print x[0][i], cost


