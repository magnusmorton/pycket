#!/usr/bin/env python

# This program attempts to cluster traces
import sys
import os.path
import numpy as np


from scipy.cluster.vq import vq, kmeans, whiten


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
             'SETINTERIORFIELD_GC_OP',
             'SETINTERIORFIELD_RAW_OP',
             'ZERO_ARRAY_OP']

int_ops = ['INCREMENT_DEBUG_COUNTER',
           'INT_LT',
           'INT_LE',
           'INT_EQ',
           'INT_NE',
           'INT_GT',
           'INT_GE',
           'UINT_LT',
           'UINT_LE',
           'UINT_GT',
           'UINT_GE',
           'INT_ADD',
           'INT_SUB',
           'INT_MUL',
           'INT_FLOORDIV',
           'UINT_FLOORDIV',
           'INT_MOD',
           'INT_AND',
           'INT_OR',
           'INT_XOR',
           'INT_RSHIFT',
           'INT_LSHIFT',
           
           'UINT_RSHIFT',
           'INT_SIGNEXT',
           'INT_IS_ZERO',
           'INT_IS_TRUE',
           'INT_NEG',
           'INT_INVERT',
           'INT_FORCE_GE_ZERO',
           'INT_ADD_OVF',
           'INT_SUB_OVF',
           'INT_MUL_OVF']

float_ops = [ 'FLOAT_ADD',
              'FLOAT_SUB',
              'FLOAT_MUL',
              'FLOAT_TRUEDIV',
              'FLOAT_NEG',
              'FLOAT_ABS']

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
    'COPYSTRCONTENT',     
    'COPYUNICODECONTENT',
    'STRGETITEM_OP']
guard = "GUARD:"
jump = "JUMP_OP"


prog_vecs = {}
for path in sys.argv[1:]:
    print path
    # create vector for classes
    prog_vec = np.zeros(8)
    with open(path, 'r') as f:
        for line in f:
            line = line.split()
            index = 99
            if line[0] in object_ops:
                index = 0
            elif line[0] in array_ops:
                index = 1
            elif line[0] in int_ops:
                index = 2
            elif line[0] in float_ops:
                index = 3
            elif line[0] in alloc_ops:
                index = 4
            elif line[0] in string_ops:
                index = 5
            elif line[0] == guard:
                index = 6
            elif line[0] == jump:
                index = 0
            else:
                continue
            prog_vec[index] = int(line[1])
    prog_vecs[os.path.basename(path)] = prog_vec

features = np.array(prog_vecs.values())
whitened = whiten(features)

print kmeans(whitened, 4)
