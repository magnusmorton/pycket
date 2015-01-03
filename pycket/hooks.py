from rpython.rlib import jit_hooks
from rpython.rlib.jit import JitHookInterface, Counters


from pycket.error import SchemeException


class PycketJitInterface(JitHookInterface):

    def after_compile(self, debug_info):
        print debug_info
            
    def before_compile(self, debug_info):
        print debug_info


