from rpython.rlib import jit, jit_hooks
from rpython.rlib.jit import JitHookInterface, Counters
from rpython.rlib.objectmodel import compute_unique_id, current_object_addr_as_int, compute_hash
from pycket.analysis.simple import Simple
#from pycket.prims.jitinfo import counters
#from pycket.prims.jitinfo import traces
from pycket.trace import Trace, Bridge
from pycket.error import SchemeException


from pycket.entry_point import toplevel_holder

class FunctionJitInterface(JitHookInterface):
    
    def __init__(self):
        super(FunctionJitInterface, self).__init__()
    def test(self):
        print "TESTING"

    def on_abort(self, reason, jitdriver, greenkey, greenkey_repr, logops, operations):
        """ A hook called each time a loop is aborted with jitdriver and
        greenkey where it started, reason is a string why it got aborted
        """
        print "ERROR"


    def on_trace_too_long(self, jitdriver, greenkey, greenkey_repr):
        print "ERROR"

    


    def before_compile(self, debug_info):
        """ A hook called after a loop is optimized, before compiling assembler,
        called with JitDebugInfo instance. Overwrite for custom behavior
        """
        print "NOT ERROR"

    def after_compile(self, debug_info):
        """ A hook called after a loop has compiled assembler,
        called with JitDebugInfo instance. Overwrite for custom behavior
        """
        # if self.foo:
        print "NOT ERROR"
        if toplevel_holder.toplevel_env.module_env.modules:
            for key,value in toplevel_holder.toplevel_env.module_env.modules.iteritems():
                if key.endswith("trace-info.rkt"):

                    from pycket.values import W_Symbol
                    from pycket.values_string import W_String
                    from pycket.cont import NilCont
                    value.defs[W_Symbol.make("foo")] = W_String.make("bar")

    def before_compile_bridge(self, debug_info):
        """ A hook called before a bridge is compiled, but after optimizations
        are performed. Called with instance of debug_info, overwrite for
        custom behavior
        """
        print "NOT ERROR"

    def after_compile_bridge(self, debug_info):
        """ A hook called after a bridge is compiled, called with JitDebugInfo
        instance, overwrite for custom behavior
        """
        print "NOT ERROR"

class AJPJitInterface(JitHookInterface):

    def after_compile(self, debug_info):
        from pycket.values import W_Symbol, w_null, W_Cons, W_Fixnum
        from pycket.hash.simple import make_simple_mutable_table, W_EqvMutableHashTable
        from pycket.cont import NilCont
        w_trace_symbol = W_Symbol.make("traces")
        w_trace = self._after_compile(debug_info)
        env = toplevel_holder.toplevel_env
        if toplevel_holder.toplevel_env.module_env.modules:
            for key,value in toplevel_holder.toplevel_env.module_env.modules.iteritems():
                if key.endswith("trace-info.rkt"):
                    print key
                    if w_trace_symbol not in value.defs:
                        value.defs[w_trace_symbol] = make_simple_mutable_table(W_EqvMutableHashTable)
                    w_traces = value.defs[w_trace_symbol]
                    w_new_traces = W_Cons.make(w_trace, w_traces)
                    w_traces.hash_set(W_Fixnum(debug_info.looptoken.number), w_new_traces, toplevel_holder.toplevel_env, NilCont())
                    break
                        
                    
                    
                    

    def after_compile_bridge(self, debug_info):
        from pycket.values import W_Symbol
        w_bridge_symbol = W_Symbol.make("bridges")
        w_bridge = self._after_compile(debug_info)

    def _after_compile(self, debug_info):
        print "getting ops..."
        from pycket.values import W_Cons, wrap_list, W_Fixnum
        from pycket.values_string import W_String
        trace = []
        for op in debug_info.operations:
            car = op.getopname()
            cdr = -1
            if car == "label" or car.startswith("guard"):
                cdr = compute_unique_id(op.getdescr())
            trace.append(W_Cons.make(W_String.make(car), W_Fixnum(cdr)))
        return wrap_list(trace)
            
            
        
class StdOutJitInterface(JitHookInterface):

    def __init__(self, analysis):
        """ sets the analysis to use"""
        super(PycketJitInterface, self).__init__()
        self.analysis = analysis

    @jit.dont_look_inside
    def after_compile(self, debug_info):
        trace_list.append(Trace(debug_info.operations))
        print "LOOP", debug_info.looptoken.repr_of_descr()
        _output(debug_info)
        #traces.append("newtrace")
    
    def after_compile_bridge(self, debug_info):
        trace_list.append(Bridge(debug_info.operations, compute_unique_id(debug_info.fail_descr)))
        print "BRIDGE: ", compute_unique_id(debug_info.fail_descr)
        _output(debug_info)

def loop_hash(operations):
    hash_num = 0
    for op in operations:
        hash_num *= 251
        hash_num += compute_hash(op.__class__.__name__)
    return hash_num


def analyse():
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


def _output(debug_info):
    for op in debug_info.operations:
        if op.getopname() == "label":
            print "LABEL: ", op.getdescr().repr_of_descr()
        elif op.getopname()[0:5] == "guard":
            print "GUARD: ", compute_unique_id(op.getdescr())
        else:
            print op
    print "END TRACE"
    print "ASSEMBLY", debug_info.asminfo.asmlen,
    print "from ops:", len(debug_info.operations)

# #pycket_hooks = PycketJitInterface(Simple())
test_hooks = FunctionJitInterface()

hooks = AJPJitInterface()
