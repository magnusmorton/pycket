class Trace(object):
    def __init__(self, ops):
        self.operations = ops
        
    def __hash__(self):
        hash_num = 0
        for op in self.operations:
            hash_num *= 251
            hash_num += compute_hash(op.__class__.__name__)
        return hash_num

class Bridge(Trace):
    def __init__(self, ops, guard):
        """ No super() in RPython """
        self.ops = ops
        self.guard = guard
