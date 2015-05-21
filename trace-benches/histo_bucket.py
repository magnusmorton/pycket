from __future__ import division
import os.path
import re
import sys

import operator


instruction_re = re.compile("<(.*) object at .*>")

for arg in sys.argv[1:]:
    histo = {}
    with open(arg, 'r') as f:
        for line in f:
            m_ins = instruction_re.match(line)
            split = line.split()
            if m_ins:
                ins = m_ins.group(1)
                if ins in histo:
                    histo[ins] += 1
                else:
                    histo[ins] = 1
            elif split and (split[0] == "LABEL:" or split[0] == "GUARD:"):
                if split[0] in histo:
                    histo[split[0]] += 1
                else:
                    histo[split[0]] = 1
    del histo["DEBUG_MERGE_POINT_OP"]            
    count = reduce(operator.add, histo.values())
    sorted_histo = sorted(histo.items(), key=operator.itemgetter(1))
    name = os.path.basename(arg)
    with open(name + "_histo.dat", "w") as f:
        for key, value in sorted_histo:
            f.write(key + " " + str(value))
            f.write("\n")
        

            
