import re
target_token_re = re.compile(".*TargetToken\((?P<tt_val>\d*)\)")

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
    cost_fn = simple_cost
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
