import re
import sys

histo = {}
instruction_re = re.compile("<(.*) object at .*>")

try:
    with open("histo.dat", 'r') as f:
        for line in f:
            stats = line.split()
            histo[stats[0]] = int(stats[1])
except:
    print "first run"

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
            

with open("histo.dat", 'w') as f:
    for key, value in histo.iteritems():
        f.write(key)
        f.write(" ")
        f.write(str(value))
        f.write("\n")
            
            
