import re
import sys

loop_re = re.compile("LOOP - HASH: (.*) TT: (.*) COST: (.*)")
bridge_re = re.compile("BRIDGE - HASH: (.*) GUARD: (.*) COST: (.*)")
for arg in sys.argv:
    print arg
    with open(arg, 'r') as f:
        for line in f:
            m = loop_re.match(line)
            print m
    
