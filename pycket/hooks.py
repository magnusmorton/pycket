from rpython.rlib import jit_hooks
from rpython.rlib.jit import JitHookInterface, Counters
from rpython.rlib.objectmodel import compute_unique_id, current_object_addr_as_int, compute_hash
from pycket.analysis.simple import Simple

from pycket.trace import Trace, Bridge

from pycket.error import SchemeException

trace_list = []

class PycketJitInterface(JitHookInterface):

    def __init__(self, analysis):
        """ sets the analysis to use"""
        super(PycketJitInterface, self).__init__()
        self.analysis = analysis
        
    def after_compile(self, debug_info):
        trace_list.append(Trace(debug_info.operations))
        print "LOOP", debug_info.looptoken.repr_of_descr()
        _output(debug_info)
    
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

pycket_hooks = PycketJitInterface(Simple())
