from rpython.rlib import jit, jit_hooks
from rpython.rlib.jit import Counters
from rpython.jit.metainterp.resoperation import rop, opname
from pycket.prims.expose import expose, default
from pycket.values import W_Cons, wrap, W_Symbol, w_null, W_Fixnum, wrap_list, W_Flonum
from pycket.values_string import W_String
from pycket.vector import wrap_vector
from pycket.hash.simple import make_simple_immutable_table, W_EqvImmutableHashTable
from pycket.entry_point import toplevel_holder
from pycket.cont import NilCont
#traces = []


# @expose("magtest")
# @jit.dont_look_inside
# def magtest(args):
    # if toplevel_holder.toplevel_env.module_env.modules:
        # print "ARRRR"
        # for key,value in toplevel_holder.toplevel_env.module_env.modules.iteritems():
            # if key.endswith("trace-info.rkt"):
                # value.defs[W_Symbol.make(u"silly")].call([],
                        # toplevel_holder.toplevel_env, NilCont())
@expose("decode-opnum", [W_Fixnum])
def decode_opnum(num):
   return W_String.make(opname[num.toint()])


@expose("class?", [W_Fixnum])
def what_class(num):
    """
    class 0 is alloc,
    class 1 is num
    class 2 is array
    class 3 is object
    class 4 is guard
    class 5 is other
    """
    if rop.is_malloc(num):
        return W_Fixnum(0)
    elif rop._ALWAYS_PURE_FIRST <= num <= rop.NURSERY_PTR_INCREMENT:
        return W_Fixnum(1)
    elif rop.GETARRAYITEM_GC <= num <= rop.GETARRAYITEM_RAW or num ==
    rop.ARRAYLEN_GC or num == rop.GETARRAYITEM_GC_PURE or num == rop.ZERO_ARRAY:
        return W_Fixnum(2)
    elif rop.RAW_STORE <= num <= rop.SETFIELD_RAW or rop.LOAD_FROM_GC_TABLE <=
    num <= rop._RAW_LOAD_LAST:
        return W_Fixnum(3)
    elif rop.is_guard(num):
        return W_Fixnum(4)
    else:
        return W_Fixnum(5)
    

@expose("asm-lengths")
@jit.dont_look_inside
def asm_lengths(args):
    w_asm_symbol = W_Symbol.make("asm")
    if toplevel_holder.toplevel_env.module_env.modules:
        for key,value in toplevel_holder.toplevel_env.module_env.modules.iteritems():
            if key.endswith("trace-info.rkt"):
                if w_asm_symbol in value.defs:
                    return value.defs[w_asm_symbol]
                else:
                    return w_null

@expose("get-trace-db")
@jit.dont_look_inside
def get_trace_db(args):
    w_trace_symbol=W_Symbol.make("traces")
    env = toplevel_holder.toplevel_env
    if toplevel_holder.toplevel_env.module_env.modules:
        for key,value in toplevel_holder.toplevel_env.module_env.modules.iteritems():
            if key.endswith("trace-info.rkt"):
                if w_trace_symbol in value.defs:
                    return value.defs[w_trace_symbol]
                else:
                    return w_null

@expose("get-guards")
@jit.dont_look_inside
def get_guards(args):
    w_guard_symbol=W_Symbol.make("guards")
    if toplevel_holder.toplevel_env.module_env.modules:
        for key,value in toplevel_holder.toplevel_env.module_env.modules.iteritems():
            if key.endswith("trace-info.rkt"):
                if w_guard_symbol in value.defs:
                    return value.defs[w_guard_symbol]
                else:
                    return w_null
                        
@expose("counters")
@jit.dont_look_inside
def counters(args):
    ll_times = jit_hooks.stats_get_loop_run_times(None)
    l_keys = []
    l_vals = []
    if ll_times:
        for i in range(len(ll_times)):
            curr = ll_times[i]
            tag = W_Fixnum(curr.number)
            count = W_Fixnum(curr.counter)
            l_keys.append(tag)
            l_vals.append(count)

    return  make_simple_immutable_table(W_EqvImmutableHashTable,l_keys, l_vals)




@expose("backend-time")
@jit.dont_look_inside
def backend_time(args):
    b_time = jit_hooks.stats_get_times_value(None, Counters.BACKEND)
    return W_Flonum(b_time)
