import re
import sys

loop_re = re.compile("LOOP - HASH: (?P<hash>.*) TT: (?P<tt>.*) COST: (?P<cost>.*)")
bridge_re = re.compile("BRIDGE -.*HASH: (?P<hash>.*) GUARD: *(?P<guard>\d*) COST: (?P<cost>.*)")
target_token_re = re.compile(".*TargetToken\((?P<tt_val>\d*)\)")
counts_re = re.compile("loop.*[lb] (?P<fragment>\d*) (?P<count>\d*)") 
times_re = re.compile("cpu time: (\d*) real time: \d* gc time: \d*")
values = []
for arg in sys.argv[1:]:
    print arg
    run = {}
    counts = {}
    times = [] 
    with open(arg, 'r') as f:
        for line in f:
            m_loop = loop_re.match(line)
            m_bridge = bridge_re.match(line)
            m_times = times_re.match(line)
            m_counts = counts_re.match(line)
            if m_loop:
                hash = m_loop.group('hash')
                cost = m_loop.group('cost')
                tt =  target_token_re.match(m_loop.group('tt')).group("tt_val")
                run[tt] = (int(hash), int(cost))
            if m_bridge:
                hash = m_bridge.group('hash')
                cost = m_bridge.group('cost')
                guard =  m_bridge.group("guard")
                run[guard] = (int(hash), int(cost))
            if m_times:
                times.append(int(m_times.group(1)))
            if m_counts:
                counts[m_counts.group("fragment")] = int(m_counts.group("count"))
                
    eqn = {}
    for key, value in counts.iteritems():
        # TODO: count bridge labels
        if key in run:
            hash, cost = run[key]
            eqn[hash] = (cost, value)
    eqn["time"] = reduce(lambda x, y: x+y, times) / float(len(times))
    print eqn
    values.append(eqn)

print len(values)
print values

                



