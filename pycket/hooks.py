from rpython.rlib import jit_hooks
from rpython.rlib.jit import JitHookInterface, Counters
from rpython.rlib.objectmodel import compute_unique_id, current_object_addr_as_int


from pycket.error import SchemeException


class PycketJitInterface(JitHookInterface):

    def __init__(self, analysis):
        """ sets the analysis to use"""
        super(PycketJitInterface, self).__init__()
        self.analysis = analysis
        

    def after_compile(self, debug_info):
        print "AFTER COMPILE"
        # assume first instruction is label
        current_label = None
        start_pos = 0
        for i, op in enumerate(debug_info.operations):
            if op.getopname() == "label":
                if current_label is not None:
                    print "TT: ", current_label.getdescr().repr_of_descr()
                    print "COST: ", str(self.analysis.cost(debug_info.operations[start_pos:i]))
                current_label = op
                start_pos = i
            if op.getopname() == "jump":
                print "TT: ", current_label.getdescr().repr_of_descr()
                print "COST: ", str(self.analysis.cost(debug_info.operations[start_pos:i]))




    def after_compile_bridge(self, debug_info):
        # in the benchmarks I use, hopefully I won't see this
        print "BRIDGE!! "
        print "GUARD: ", compute_unique_id(debug_info.fail_descr)
        print "COST: ", str(self.analysis.cost(debug_info.operations))


        
