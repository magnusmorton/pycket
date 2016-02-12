from rpython.rlib import jit, jit_hooks

from pycket.prims.expose import expose, default
from pycket.values import W_Cons


@expose("counters")
@jit.dont_look_inside
def counters(args):
    times = jit_hooks.stats_get_loop_run_times(None)
    return W_Cons()
