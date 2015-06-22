import argparse
from itertools import izip

import trace_parser
import trace as trace_utils


def produce_gnuplot_file(costs, times, names):
    with open("whole_program.dat", "w") as f:
        for cost, time, name in izip(costs, times, names):
            f.write(str(cost) + " " + str(time) + " " +  name + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run cost analysis")
    parser.add_argument("filenames", metavar="<file>", nargs = '+')
    parser.add_argument("--model", "-m",  default="cm1")



    args = parser.parse_args()
    model = []
    if args.model == "cm0":
        model = [0,0,0,0,0]
    elif args.model == "cm1":
        model = [1,1,1,1,1]
    elif args.model == "cm2":
        model = [10,1,1,10,1]
    else:
        model = [int(num) for num in args.model.split(",")]
    average_times = trace_parser.calculate_average_times()
    programs = trace_parser.parse_files(args.filenames)
    counts = {program.name: program.class_counts() for program in programs}
    dot = lambda x,y: sum(a*b for a,b in izip(x,y))
    trace_utils.Fragment.model = model
    costs = [dot(counts[program.name], model) for program in programs]
    if model == [0,0,0,0,0]:
        print "FOOOOOO"
        costs = [program.cost() for program in programs]
    times = [average_times[program.name] for program in programs]
    names = [program.name for program in programs]
    produce_gnuplot_file(costs, times,names)
    

    
if __name__ == '__main__':
    main()
