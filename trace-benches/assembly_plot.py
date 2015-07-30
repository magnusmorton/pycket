import argparse
import matplotlib.pyplot as plt

import trace_parser

def main():
    parser = argparse.ArgumentParser(description="Compare assembly to jit ops")
    parser.add_argument("filenames", metavar="<file>", nargs = '+')

    args = parser.parse_args()

    traces = trace_parser.parse_files(args.filenames, fragment=True)
    print len(traces)
    assembly_counts = [trace.assembly_count for trace in traces if len(trace.ops) < 5000]
    op_counts = [len(trace.ops) for trace in traces if len(trace.ops) < 5000]
    plt.ylabel("Assembly counts")
    plt.xlabel("op counts")
    plt.title("Assembly vs op counts")
    plt.scatter(op_counts, assembly_counts)
    plt.show()
    return 0

if __name__ == '__main__':
    main()
