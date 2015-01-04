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
        self.analysis.set_trace(debug_info.operations)
        print "TRACE COST: "
        print str(self.analysis.cost())
            
    def before_compile(self, debug_info):
        print "BEFORE COMPILE"


