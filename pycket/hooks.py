from rpython.rlib import jit_hooks
from rpython.rlib.jit import JitHookInterface, Counters
from rpython.rlib.objectmodel import compute_unique_id, current_object_addr_as_int


from pycket.error import SchemeException


class PycketJitInterface(JitHookInterface):

    def __init__(self, analysis):
        """ sets the analysis to use"""
        print "NEW ANALYSIS"
        print "============"
        super(PycketJitInterface, self).__init__()
        self.analysis = analysis
        

    def after_compile(self, debug_info):
        print "AFTER COMPILE"
        print "LOOP TOKEN: ", debug_info.looptoken.__repr__()
        
               
        # assume first instruction is label
        current_label = None
        start_pos = 0
        for i, op in enumerate(debug_info.operations):
            if op.getopname() == "label":
                tt = op.getdescr()
                print "TT: ", tt.repr_of_descr()
                if current_label is not None:
                    self.analysis.set_trace(debug_info.operations[start_pos:i])
                    print "COST: ", str(self.analysis.cost())
                current_label = op
                start_pos = i
            if op.getopname() == "jump":
                self.analysis.set_trace(debug_info.operations[start_pos:i])
                print "COST: ",  str(self.analysis.cost())




    def after_compile_bridge(self, debug_info):
        # in the benchmarks I use, hopefully I won't see this
        print "BRIDGE!! "
        print "LOOP TOKEN: ", debug_info.looptoken.__repr__()
        self.analysis.set_trace(debug_info.operations)
        print "TRACE COST: "
        print str(self.analysis.cost())


        
