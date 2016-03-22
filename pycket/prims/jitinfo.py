from rpython.rlib import jit, jit_hooks

from pycket.prims.expose import expose, default
from pycket.values import W_Cons, wrap, W_Symbol
from pycket.values_string import W_String
from pycket.vector import wrap_vector
from pycket.hash.simple import make_simple_immutable_table
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


@expose("counters")
@jit.dont_look_inside
def counters(args):
    def bar():
        print "bar"
    print "HELLO!!!111"
    print toplevel_holder.toplevel_list
    print "HELLO AGAIN"
    # if counters.foo:
        # for fo in counters.foo:
    # for key,value in toplevel_holder.toplevel_env.module_env.modules.iteritems():
        # if key.endswith("fib-traces.rkt"):
            # print "in fib-traces"
            # from pycket.values import W_Symbol
            # from pycket.cont import NilCont
            # # value.defs[W_Symbol.make("bar")].call([],
                    # # toplevel_holder.toplevel_env, NilCont())        # print fo
            # value.defs[W_Symbol.make("foo")] = W_String.make("bar")
    print "AND AGAIN"
    # traces = get_traces()
    # assert traces is not None
    # if traces:
        # print "there are some traces"
        # trace = traces.value
        # if trace:
            # print "trace"
            # print trace
    # ll_times = jit_hooks.stats_get_loop_run_times(None)
    # e_keys = []
    # e_vals = []
    # l_keys = []
    # l_vals = []
    # b_keys = []
    # b_vals = []
    # if ll_times:
        # for i in range(len(ll_times)):
            # curr = ll_times[i]
            # print "foo"
            # print "foo,", ll_times[i].counter
            # print curr.counter
            # # tag = wrap(curr.number)
    #         count = wrap(curr.counter)
    #         if curr.type == 'e':
    #             e_keys.append(tag)
    #             e_vals.append(count)
    #         elif curr.type == 'l':
    #             l_keys.append(tag)
    #             l_vals.append(count)
    #         elif curr.type == 'b':
    #             b_keys.append(tag)
    #             b_vals.append(count)

    # e_hash = make_simple_immutable_table(wrap(e_keys), wrap(e_vals))
    # l_hash = make_simple_immutable_table(wrap(l_keys), wrap(l_vals))
    # b_hash = make_simple_immutable_table(wrap(b_keys), wrap(b_vals))
    
    # return wrap_vector([e_hash,l_hash,b_hash])
