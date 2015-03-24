import re
import sys

histo = {}
instruction_re = re.compile("<(.*) object at .*>")

for arg in sys.argv[1:]:
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
            elif split[0] == "LABEL:" or split[0] == "GUARD:":
                if split[0] in histo:
                    histo[split[0]] += 1
                else:
                    histo[split[0]] = 1
            

for key, value in histo.iteritems():
    print key, value

            
