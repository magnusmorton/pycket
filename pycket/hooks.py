from rpython.rlib import jit_hooks
from rpython.rlib.jit import JitHookInterface, Counters
from rpython.rlib.objectmodel import compute_unique_id, current_object_addr_as_int, compute_hash


from pycket.error import SchemeException


class PycketJitInterface(JitHookInterface):

    def __init__(self, analysis):
        """ sets the analysis to use"""
        super(PycketJitInterface, self).__init__()
        self.analysis = analysis
        

    def after_compile(self, debug_info):
        print "LOOP"
        # assume first instruction is label
        current_label = None
        start_pos = 0
        for i, op in enumerate(debug_info.operations):
            if op.getopname() == "label":
                if current_label is not None:
                    print "LOOP - HASH: ", loop_hash(debug_info.operations[start_pos:i]), " TT: ", current_label.getdescr().repr_of_descr(), " COST: ", str(self.analysis.cost(debug_info.operations[start_pos:i]))
                current_label = op
                start_pos = i
            if op.getopname() == "jump":
                if current_label is not None:
                    print "LOOP - HASH: ", loop_hash(debug_info.operations[start_pos:i]), " TT: ", current_label.getdescr().repr_of_descr(), " COST: ", str(self.analysis.cost(debug_info.operations[start_pos:i]))


    def after_compile_bridge(self, debug_info):
        # in the benchmarks I use, hopefully I won't see this
        print "BRIDGE -  HASH: ", loop_hash(debug_info.operations), " GUARD: ", compute_unique_id(debug_info.fail_descr), " COST: ", str(self.analysis.cost(debug_info.operations))




def loop_hash(operations):
    hash_num = 0
    for op in operations:
        hash_num *= 251
        hash_num += compute_hash(op.__class__.__name__)
    return hash_num
