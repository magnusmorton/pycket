import instructions
import re
import operator as op

target_token_re = re.compile(r".*TargetToken\((?P<tt_val>\d*)\)")

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

def deriv_cost(frag, i=None):
    if not i:
        i = len(frag.ops)
    j = 0
    cost = 0
    while j < i:
        op = frag.ops[j].split()[0]
        if op in instructions.object_ops:
            cost += 861
        elif op == "GUARD:":
            cost += 88
        elif op != "DEBUG_MERGE_POINT_OP":
            cost += 1
        j += 1
    return cost

def null_cost(frag, i=None):
    return 1
        
        

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
    model = None
    def __init__(self, ops, label, guards):
        self.ops = ops
        self.label = label
        self.guards = guards

    def class_counts(self, i=None):
        if not i:
            i = len(self.ops)
        j = 0
        counts = [0]*5
        while j < i:
            op = self.ops[j].split()[0]
            if op in instructions.object_ops:
                counts[0] += 1
            elif op in instructions.array_ops:
                counts[1] += 1
            elif op in instructions.num_ops:
                counts[2] += 1
            elif op in instructions.alloc_ops:
                counts[3] += 1
            elif op == "GUARD:":
                counts[4] += 1
            j += 1
        return counts


    def count2guard(self, guard):
        return self.class_counts(self.guards[guard])

    def cost_with_model(self, i=None):
        if not Fragment.model:
            raise "Model not defined"
        if Fragment.model == (0,0,0,0,0):
            return 1
        # order is [order, array, num, alloc, guards]
        if not i:
            i = len(self.ops)
        j = 0
        cost = 0
        while j < i:
            op = self.ops[j].split()[0]
            if op in instructions.object_ops:
                cost += Fragment.model[0]
            elif op in instructions.array_ops:
                cost += Fragment.model[1]
            elif op in instructions.num_ops:
                cost += Fragment.model[2]
            elif op in instructions.alloc_ops:
                cost += Fragment.model[3]
            elif op == "GUARD:":
                cost += Fragment.model[4]
            j += 1
        return cost

    cost_fn = cost_with_model
        
        

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

class Program(object):
    def __init__(self, name, fragments, counts, entry_points):
        self.name = name
        self.fragments = fragments
        self.counts = counts
        self.entry_points = entry_points

    def cost(self):
        frag_costs = {}
        eqn = {}
        for key, value in self.counts.iteritems():
            if value:
                if key in self.fragments:
                    frag = self.fragments[key]
                    for key2,value2 in self.counts.iteritems():
                        if key2 in frag.guards:
                            guard_cost = frag.cost2guard(key2)
                            value = value - value2
                            # bug here - just add the key instead
                            eqn[hash(frag) + hash(key2)] = value2
                            frag_costs[hash(frag) + hash(key2)] = guard_cost
                    eqn[hash(frag)] =  value
                    frag_costs[hash(frag)] = frag.cost()

        # special case for loops with no labels
        if len(self.fragments) > len(self.counts):
            for key, value in self.fragments.iteritems():
                if key in self.entry_points:
                    count = self.entry_points[key]
                    if count:
                        for key2,value2 in self.counts.iteritems():
                            if key2 in frag.guards:
                                guard_cost = frag.cost2guard(key2)
                                count = count - value2
                                eqn[hash(value) + hash(key2)] = value2
                                frag_costs[hash(value) + hash(key2)] = guard_cost
                        eqn[hash(value)] = count
                        frag_costs[hash(frag)] = frag.cost()

        return reduce(lambda x, y: x + eqn[y] * frag_costs[y], eqn,0)

    def class_counts(self):
        frag_counts = {}
        eqn = {}
        for key, value in self.counts.iteritems():
            if value:
                if key in self.fragments:
                    frag = self.fragments[key]
                    for key2,value2 in self.counts.iteritems():
                        if key2 in frag.guards:
                            guard_count = frag.count2guard(key2)
                            value = value - value2
                            eqn[hash(frag) + hash(key2)] = value2
                            frag_counts[hash(frag) + hash(key2)] = guard_count
                    eqn[hash(frag)] =  value
                    frag_counts[hash(frag)] = frag.class_counts()

        # special case for loops with no labels
        if len(self.fragments) > len(self.counts):
            for key, value in self.fragments.iteritems():
                if key in self.entry_points:
                    count = self.entry_points[key]
                    if count:
                        for key2,value2 in self.counts.iteritems():
                            if key2 in frag.guards:
                                guard_count = frag.count2guard(key2)
                                count = count - value2
                                eqn[hash(value) + hash(key2)] = value2
                                frag_counts[hash(value) + hash(key2)] = guard_count
                        eqn[hash(value)] = count
                        frag_counts[hash(frag)] = frag.class_counts()

        # sum all lists in frag_counts
        add_lists = lambda a, b: map(op.add, a, b)
        scal_mul = lambda s, a: [s*i for i in a]
        return reduce( lambda x, y: add_lists(x, scal_mul(eqn[y], frag_counts[y])), eqn, [0,0,0,0,0])

            
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
