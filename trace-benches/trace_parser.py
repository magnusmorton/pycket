import csv
import operator
import os.path
import re

import trace as trace_utils

loop_re = re.compile(r"LOOP - HASH: (?P<hash>.*) TT: (?P<tt>.*) COST: (?P<cost>.*)")
bridge_re = re.compile(r"BRIDGE -.*HASH: (?P<hash>.*) GUARD: *(?P<guard>\d*) COST: (?P<cost>.*)")
counts_re = re.compile(r"loop.*([elb]) (?P<fragment>\d*) (?P<count>\d*)") 
times_re = re.compile(r"\s*(\d*\.\d*) seconds time elapsed")
looptoken_re = re.compile(r"<Loop(\d*)>")


def calculate_average_times():
    tsv_paths = ["CrossBenchmarks_pycket.tsv", "Shootout_pycket.tsv"]
    times_dict = {}
    for tsv_path in tsv_paths:
        with open(tsv_path, "r") as f:
            tsv = csv.reader(f, delimiter = "\t")
            for line in tsv:
                # line[4] is the name of the benchmark
                if len(line) >= 5 and line[3] == "total":
                    if line[4] not in times_dict:
                        times_dict[line[4]] = []
                        times_dict[line[4]].append(float(line[1]))
    return {name: sum(times)/float(len(times)) for name, times in times_dict.iteritems()}


def parse_files(filenames):
    all_traces = []
    for arg in filenames:
        #print arg
        counts = {}
        run_times = [] 
        traces = []
        guards = []
        entry_points = {}
        with open(arg, 'r') as f:
            line = f.readline()
            while line:
                if line == "BEGIN":
                    # we only need the last instance of these
                    counts = {}
                    traces = []
                    guards = []
                    entry_points = {}
                m_times = times_re.match(line)
                m_counts = counts_re.match(line.rstrip())
                if line[0:4] == 'LOOP':
                    tokens = line.split()
                    looptoken = int(looptoken_re.match(tokens[1]).group(1))
                    traces.append(trace_utils.build_trace(f, token=looptoken))
                elif line[0:6] == 'BRIDGE':
                    tokens = line.split()
                    guard = tokens[1]
                    traces.append(trace_utils.build_trace(f, guard=guard))
                if m_times:
                    run_times.append(float(m_times.group(1)))
                if m_counts:
                    count = float(m_counts.group("count"))
                    if count > 0:
                        if m_counts.group(1) == 'e':
                            entry_points[int(m_counts.group("fragment"))] = count
                        counts[int(m_counts.group("fragment"))] = count
                        if m_counts.group(1) == 'b':
                            guards.append(int(m_counts.group("fragment")))
                line = f.readline()


        # build fragments for each trace, flatten the list and turn it into a dic
        frags = {frag.label: frag for frag in reduce(operator.add, [trace.get_fragments(guards) for trace in traces])}
        name = os.path.basename(arg)
        all_traces.append(trace_utils.Program(name, frags, counts, entry_points))
    return all_traces
