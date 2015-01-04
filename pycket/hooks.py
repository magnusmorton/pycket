from rpython.rlib import jit_hooks
from rpython.rlib.jit import JitHookInterface, Counters


from pycket.error import SchemeException


class PycketJitInterface(JitHookInterface):

    def __init__(self, analysis):
        """ sets the analysis to use"""
        super(PycketJitInterface, self).__init__()
        self.analysis = analysis

    def after_compile(self, debug_info):
        print "AFTER COMPILE"
        print "LOOP TOKEN: ", repr(debug_info.looptoken)
        self.analysis.set_trace(debug_info.operations)
        print "TRACE COST: "
        print str(self.analysis.cost())


    def after_compile_bridge(self, debug_info):
        # in the benchmarks I use, hopefully I won't see this
        print "BRIDGE!! "
        print "LOOP TOKEN: ", repr(debug_info.looptoken)
        self.analysis.set_trace(debug_info.operations)
        print "TRACE COST: "
        print str(self.analysis.cost())
