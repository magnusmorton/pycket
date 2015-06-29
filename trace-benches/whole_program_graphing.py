import argparse
import sys
from itertools import izip
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np
import trace_parser
import trace as trace_utils


dot = lambda x,y: sum(a*b for a,b in izip(x,y))

def produce_gnuplot_file(costs, times, names):
    k_stats(costs, times, names)
    with open("whole_program.dat", "w") as f:
        for cost, time, name in izip(costs, times, names):
            f.write(str(cost) + " " + str(time) + " " +  name + " " + str(time / cost) +  "\n")



def k_stats(costs, times, names):
    ks = np.array([time/cost for cost, time in izip(costs, times)])
    print "Mean: " + np.mean(ks) + " STD DEV: " + np.std(ks)
    
def graph_k_scaling(costs0, costsc, costsw, times, names):
    width = 0.2333
    ind = np.arange(len(names))
    ks0 = np.array([time/cost for time, cost in izip(times, costs0)])
    ksc = np.array([time/cost for time, cost in izip(times, costsc)])
    ksw = np.array([time/cost for time, cost in izip(times, costsw)])
    rects0 = plt.bar(ind, ks0, width, color='r')
    rectsc = plt.bar(ind+width, ksc, width, color='g')
    rectsw = plt.bar(ind+ 2*width, ksw, width, color='b')
    plt.ylabel("k")
    plt.title("k for each benchmark")
    plt.xticks(ind + 1.5*width, names, rotation=30, ha = 'right')
    plt.yscale('log')
    plt.legend((rects0[0], rectsc[0], rectsw[0]), ("CM0", "CMC", "CMW"))
    plt.show()


def k_graph(filenames):
    cm0 = [0,0,0,0,0]
    cmc = [1,1,1,1,1]
    cmw = [1.0, 0, 5.195, 35.56,0]
    average_times = trace_parser.calculate_average_times()
    programs = trace_parser.parse_files(filenames)
    counts = {program.name: program.class_counts() for program in programs}
    
    trace_utils.Fragment.model = cm0
    costsc = [dot(counts[program.name], cmc) for program in programs]
    costsw = [dot(counts[program.name], cmw) for program in programs]
    
    costs0 = [program.cost() for program in programs]
    times = [average_times[program.name] for program in programs]
    names = [program.name for program in programs]
    graph_k_scaling(costs0, costsc,costsw, times, names)
    sys.exit(0)
    

def superimpose(costs1, costs2, times,names):
    axes = [plt, plt.twiny()]
    colors = ('g', 'b')
    offsets = (20,-20)
    for ax, color, costs, offset in izip(axes, colors, [costs1,costs2], offsets):

        #parameter, covariance_matrix = curve_fit(line_func, times, costs)
        m, b = np.polyfit(costs, times, 1)
        fit_fn = np.poly1d((m,b))
        ax.plot( costs[:10], times[:10],  'o' + color, costs, fit_fn(costs), '-' + color)
        for name, x,y in izip(names[:10], costs[:10], times[:10]):
            plt.annotate(
                name,
                xy =(x,y),
                xytext =(20,offset),
                textcoords = 'offset points', ha = 'left', va = 'bottom',
                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
        #ax.plot(x, line_func(x, *parameter), color=color)
    plt.show()


def line_func(x, a, b):
    return a*x + b

def super_graph(filenames):
    cm0 = [0,0,0,0,0]
    cmc = [1,1,1,1,1]
    cmw = [1.0, 0, 5.195, 35.56,0]
    average_times = trace_parser.calculate_average_times()
    programs = trace_parser.parse_files(filenames)
    counts = {program.name: program.class_counts() for program in programs}
    
    trace_utils.Fragment.model = cm0
    costsc = [dot(counts[program.name], cmc) for program in programs]
    costsw = [dot(counts[program.name], cmw) for program in programs]
    
    costs0 = [program.cost() for program in programs]
    times = [average_times[program.name] for program in programs]
    names = [program.name for program in programs]
    superimpose(costsc,costsw, times, names)
    sys.exit(0)
    
def main():
    parser = argparse.ArgumentParser(description="Run cost analysis")
    parser.add_argument("filenames", metavar="<file>", nargs = '+')
    parser.add_argument("--model", "-m",  default="cm1")
    parser.add_argument( "-k",  action='store_true')
    parser.add_argument( "-s",  action='store_true')
    

    args = parser.parse_args()
    if args.k:
        k_graph(args.filenames)
    if args.s:
        super_graph(args.filenames)
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
