import argparse
import matplotlib.pyplot as plt
from itertools import izip
import trace_parser

dot = lambda x,y: sum(a*b for a,b in izip(x,y))
def main():
    parser = argparse.ArgumentParser(description="Compare assembly to jit ops")
    parser.add_argument("filenames", metavar="<file>", nargs = '+')
    parser.add_argument("--model", "-m",  default="cmw")
    parser.add_argument("--text", "-t", action='store_true')

    args = parser.parse_args()
    
    if args.model == "cm0":
        model = [0,0,0,0,0]
    elif args.model == "cmc":
        model = [1,1,1,1,1]
    elif args.model == "cmw":
        model = [211,34,590,9937,14]
    else:
        model = [int(num) for num in args.model.split(",")]
    traces = trace_parser.parse_files(args.filenames, fragment=True)
    print len(traces)
    assembly_counts = [trace.assembly_count for trace in traces if len(trace.ops) < 5000]
    class_counts = [trace.class_counts() for trace in traces if len(trace.ops) < 5000]
    costs = [dot(count, model) for count in class_counts]
    if args.text:
        print "COST\tASSEMBLY"
        for cost, assembly in izip(costs,assembly_counts):
            print str(cost) + '\t' + str(assembly)
        return
    plt.ylabel("Assembly counts")
    plt.xlabel("Cost")
    plt.title("Assembly vs Cost")
    plt.scatter(costs, assembly_counts)
    plt.show()
    return 0

if __name__ == '__main__':
    main()
