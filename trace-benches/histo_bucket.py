from __future__ import division
import os.path
import re
import sys
import numpy as np
import numpy.linalg as linalg
import scipy.optimize.nnls
import operator

# numpy elements map to the following in index order
object_ops = [
    
    'GETFIELD_GC_PURE_OP',
    'GETFIELD_RAW_PURE_OP',
    
    'GETINTERIORFIELD_GC_OP',
    'RAW_LOAD_OP',
    'GETFIELD_GC_OP',
    'GETFIELD_RAW_OP',
    


    'RAW_STORE_OP',
    'SETFIELD_GC_OP',
    'SETINTERIORFIELD_GC_OP',
    'SETINTERIORFIELD_RAW_OP',
    'ZERO_PTR_FIELD_OP' # only emitted by the rewrite, clears a pointer field
                        # at a given constant offset, no descr
    ]


array_ops = ['ARRAYLEN_GC_OP',
             'GETARRAYITEM_GC_OP',
             'GETARRAYITEM_RAW_OP',
             'GETARRAYITEM_GC_PURE_OP',
             'GETARRAYITEM_RAW_PURE_OP',
             'SETARRAYITEM_GC_OP',
             'SETARRAYITEM_RAW_OP',
             
             'ZERO_ARRAY_OP']

num_ops = ['INCREMENT_DEBUG_COUNTER_OP',
           'INT_LT_OP',
           'INT_LE_OP',
           'INT_EQ_OP',
           'INT_NE_OP',
           'INT_GT_OP',
           'INT_GE_OP',
           'UINT_LT_OP',
           'UINT_LE_OP',
           'UINT_GT_OP',
           'UINT_GE_OP',
           'INT_ADD_OP',
           'INT_SUB_OP',
           'INT_MUL_OP',
           'INT_FLOORDIV_OP',
           'UINT_FLOORDIV_OP',
           'INT_MOD_OP',
           'INT_AND_OP',
           'INT_OR_OP',
           'INT_XOR_OP',
           'INT_RSHIFT_OP',
           'INT_LSHIFT_OP',
           
           'UINT_RSHIFT_OP',
           'INT_SIGNEXT_OP',
           'INT_IS_ZERO_OP',
           'INT_IS_TRUE_OP',
           'INT_NEG_OP',
           'INT_INVERT_OP',
           'INT_FORCE_GE_ZERO_OP',
           'INT_ADD_OVF_OP',
           'INT_SUB_OVF_OP',
           'INT_MUL_OVF_OP',
           'FLOAT_ADD_OP',
           'FLOAT_SUB_OP',
           'FLOAT_MUL_OP',
           'FLOAT_TRUEDIV_OP',
           'FLOAT_NEG_OP',
           'FLOAT_ABS_OP']


alloc_ops = ['NEW_OP',             #-> GcStruct, gcptrs inside are zeroed (not the rest)
             'NEW_WITH_VTABLE_OP',  #-> GcStruct with vtable, gcptrs inside are zeroed
             'NEW_ARRAY_OP',       #-> GcArray, not zeroed. only for arrays of primitives
             'NEW_ARRAY_CLEAR_OP', #-> GcArray, fully zeroed
             'NEWSTR_OP',           #-> STR, the hash field is zeroed
             'NEWUNICODE_OP']      #-> UNICODE, the hash field is zeroed]

string_ops = [ 
    'UNICODELEN_OP',
    'UNICODEGETITEM_OP',
    'STRLEN_OP',
    'COPYSTRCONTENT_OP',     
    'COPYUNICODECONTENT_OP',
    'STRGETITEM_OP']

instruction_re = re.compile("<(.*) object at .*>")
times_re = re.compile("cpu time: (\d*) real time: \d* gc time: \d*")
values = []
times = []
for arg in sys.argv[1:]:
    print arg
    histo = {"OBJ":0, "ARRAY":0, "NUM":0, "ALLOC":0, "GUARDS":0 }
    with open(arg, 'r') as f:
        for line in f:
            m_ins = instruction_re.match(line)
            m_times = times_re.match(line.rstrip())
            split = line.split()
            if m_ins:
                ins = m_ins.group(1)
                if ins in object_ops:
                    histo["OBJ"] += 1
                elif ins in array_ops:
                    histo["ARRAY"] += 1
                elif ins in num_ops:
                    histo["NUM"] += 1
                elif ins in alloc_ops:
                    histo["ALLOC"] += 1
            elif split and split[0] == "GUARD:":
                histo["GUARDS"] += 1
            elif m_times:
                times.append(float(m_times.group(1)))

    values.append(histo.values())
    print histo

print values
print times
a = np.array(values)
b = np.array(times)
x = scipy.optimize.nnls(a, b)
y = linalg.solve(a,b)
print x
print y
