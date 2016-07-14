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

    def _store_trace(self,keys, frags, guards, w_key, w_asmlen):
        from pycket.values import w_null, W_Cons, W_Fixnum, W_Symbol
        from pycket.hash.simple import make_simple_mutable_table, W_EqvMutableHashTable
        from pycket.cont import NilCont
        w_symbol = W_Symbol.make("traces")
        w_guard_symbol = W_Symbol.make("guards")
        w_asm_symbol = W_Symbol.make("asm")
        env = toplevel_holder.toplevel_env
        if toplevel_holder.toplevel_env.module_env.modules:
            #TODO: Improve performance
            for path,value in toplevel_holder.toplevel_env.module_env.modules.iteritems():
                if path.endswith("trace-info.rkt"):
                    print path
                    if w_symbol not in value.defs:
                        value.defs[w_symbol] = make_simple_mutable_table(W_EqvMutableHashTable)
                    if w_guard_symbol not in value.defs:
                        value.defs[w_guard_symbol] = make_simple_mutable_table(W_EqvMutableHashTable)
                    if w_asm_symbol not in value.defs:
                        value.defs[w_asm_symbol] = make_simple_mutable_table(W_EqvMutableHashTable)
                    
                    w_traces = value.defs[w_symbol]
                    w_guards = value.defs[w_guard_symbol]
                    w_asmlens = value.defs[w_asm_symbol]
                    w_asmlens.hash_set(w_key, w_asmlen, toplevel_holder.toplevel_env, NilCont())
                    for i, key in enumerate(keys):
                        w_traces.hash_set(key, frags[i], toplevel_holder.toplevel_env, NilCont())
                        w_guards.hash_set(key, guards[i], toplevel_holder.toplevel_env, NilCont())
                    break

    def after_compile(self, debug_info):
        from pycket.values import W_Symbol, w_null, W_Cons, W_Fixnum
        self._after_compile(debug_info, debug_info.looptoken.number)
         
    def after_compile_bridge(self, debug_info):
        from pycket.values import W_Symbol
        self._after_compile(debug_info,compute_unique_id(debug_info.fail_descr))
       
    def _after_compile(self, debug_info, key):
        from pycket.values import W_Fixnum, wrap_list, W_Cons
        from pycket.values_string import W_String
        frags = []
        keys = []
        current_frag = []
        guards = []
        current_guards = []
        current_key = W_Fixnum(key)
        for i,op in enumerate(debug_info.operations):
            opname = op.getopname()
            if opname == "label":
                frags.append(wrap_list(current_frag))
                guards.append(wrap_list(current_guards))
                keys.append(current_key)
                current_frag = []
                current_guards = []
                current_key = W_Fixnum(compute_unique_id(op.getdescr()))
            if opname == "jump":
                frags.append(wrap_list(current_frag))
                guards.append(wrap_list(current_guards))
                keys.append(current_key)
                current_frag = []
                current_guards = []
                current_key = W_Fixnum(compute_unique_id(op.getdescr()))
            if opname.startswith("guard"):
                current_guards.append(W_Cons.make(W_Fixnum(compute_unique_id(op.getdescr())), W_Fixnum(i)))
            current_frag.append(W_String.make(opname))
        self._store_trace(keys, frags, guards, W_Fixnum(key), W_Fixnum(debug_info.asminfo.asmlen))
                
            
            
        
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
