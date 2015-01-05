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
        print "LOOP TOKEN: ", debug_info.looptoken.__repr__()
        self.analysis.set_trace(debug_info.operations)
        print "TRACE COST: "
        print str(self.analysis.cost())
        print "TIMES: "
        print jit_hooks.stats_get_loop_run_times(None)
        print "COUNTERS: "
        for i, counter_name in enumerate(Counters.counter_names):
            v = jit_hooks.stats_get_counter_value(None, i)
            print v
        tr_time = jit_hooks.stats_get_times_value(None, Counters.TRACING)
        print "TRACING: "
        print tr_time


    def after_compile_bridge(self, debug_info):
        # in the benchmarks I use, hopefully I won't see this
        print "BRIDGE!! "
        print "LOOP TOKEN: ", debug_info.looptoken.__repr__()
        self.analysis.set_trace(debug_info.operations)
        print "TRACE COST: "
        print str(self.analysis.cost())

        
