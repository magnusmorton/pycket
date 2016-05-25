from rpython.rlib import jit, jit_hooks

from pycket.prims.expose import expose, default
from pycket.values import W_Cons, wrap, W_Symbol, w_null, W_Fixnum, wrap_list
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



