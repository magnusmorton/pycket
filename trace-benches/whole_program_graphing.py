import argparse
import sys
from itertools import izip
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np
import trace_parser
import trace as trace_utils
import string
import pdb

dot = lambda x,y: sum(a*b for a,b in izip(x,y))

def produce_gnuplot_file(costs, times, names):
    k_stats(costs, times, names)
    with open("whole_program.dat", "w") as f:
        for cost, time, name in izip(costs, times, names):
            f.write(str(cost) + " " + str(time) + " " +  name + " " + str(time / cost) +  "\n")



def k_stats(costs, times, names):
    ks = np.array([time/cost for cost, time in izip(costs, times)])
    print "Mean: " + str(np.mean(ks)) + " STD DEV: " + str(np.std(ks))
    
def graph_residual(costs0, costsc, costsw, times, names):
    width = 0.2333
    ind = np.arange(len(names))
    fn0 = np.poly1d(np.polyfit(costs0,times, 1))
    fnc = np.poly1d(np.polyfit(costsc,times, 1))
    fnw = np.poly1d(np.polyfit(costsw,times, 1))
    res0 = np.subtract(times, fn0(costs0))
    resc = np.subtract(times, fnc(costsc))
    resw = np.subtract(times, fnw(costsw))
    rects0 = plt.bar(ind, res0, width, color='r', hatch='/')
    rectsc = plt.bar(ind+width, resc, width, color='g', hatch='-')
    rectsw = plt.bar(ind+ 2*width, resw, width, color='b', hatch='\\')
    plt.ylabel("Residual")
    plt.xlabel("Benchmark")
    plt.title("Residuals for each benchmark")
    tick_names = [string.replace(name, "generic", "gen") for name in names]
    plt.xticks(ind + 1.5*width, tick_names, rotation=20, ha = 'right')
    outliers = ["fibfp", "heapsort", "ack", "divrec", "fib", "lattice", "trav2", "tak"]
    plt.legend((rects0[0], rectsc[0], rectsw[0]), ("CM0", "CMC", "CMW"), title="Cost Model")   
    for rect0,rectc,rectw, name in izip(rects0,rectsc,rectsw, names):
        if name in outliers:
            rect0.set(hatch='*', alpha=0.50)
            rectc.set(hatch='*', alpha=0.50)
            rectw.set(hatch='*', alpha=0.50)

    plt.show()


def residual_graph(filenames):
    cm0 = [0,0,0,0,0]
    cmc = [1,1,1,1,1]
    cmw = [15.07, 2.43, 42.14, 709.79,1]
    average_times = trace_parser.calculate_average_times()
    programs = trace_parser.parse_files(filenames)
    counts = {program.name: program.class_counts() for program in programs}
    
    trace_utils.Fragment.model = cm0
    costsc = [dot(counts[program.name], cmc) for program in programs]
    costsw = [dot(counts[program.name], cmw) for program in programs]
    
    costs0 = [program.cost() for program in programs]
    times = [average_times[program.name] for program in programs]
    names = [program.name for program in programs]
    graph_residual(costs0, costsc,costsw, times, names)
    sys.exit(0)


def rsquared(coeffs, x,y ):
    # Polynomial Coefficients
    results = {}
    results['polynomial'] = coeffs.tolist()

    # r-squared
    p = np.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)                         # or [p(z) for z in x]
    ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot

    return results

def graph(costs, times, names, model):
    outliers = ["fibfp", "heapsort", "ack", "divrec", "fib", "lattice", "trav2", "tak"]
    filtered_names = [name for name in names if name not in outliers]
    filtered_costs = [ cost for cost,name in izip(costs, names) if name in filtered_names]
    filtered_times = [time for time, name in izip(times, names) if name in filtered_names]
    outlier_costs = [cost for cost, name in izip(costs, names) if name in outliers]
    outlier_times = [time for time, name in izip(times, names) if name in outliers]
    coeffs = np.polyfit(filtered_costs, filtered_times, 1)
    fit_fn = np.poly1d(coeffs)
    k_stats(costs, times, names)
    print fit_fn
    print "rsquared"
    print rsquared(coeffs, filtered_costs, filtered_times)
    plt.ylabel("Execution time ($\mu s$)")
    plt.xlabel("Cost")
    plt.title("Whole program plot for " + model.upper())
    plt.plot( filtered_costs, filtered_times,  'xg', label="Points included in fit" )
    plt.plot(filtered_costs, fit_fn(filtered_costs), '-b')
    plt.plot( outlier_costs, outlier_times, 'or', label="Points excluded by subsampling")
    #plt.legend()
    plt.show()
    

def superimpose(costs1, costs2, times,names):
    axes = [plt, plt.twiny()]
    colors = ('g', 'b')
    offsets = (20,-20)
    for ax, color, costs, offset in izip(axes, colors, [costs1,costs2], offsets):

        #parameter, covariance_matrix = curve_fit(line_func, times, costs)
        m, b = np.polyfit(costs, times, 1)
        fit_fn = np.poly1d((m,b))
        ax.plot( costs[:10], times[:10],  'o' + color, costs, fit_fn(costs), '-' + color)
        print fit_fn
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
    cmw = [211,34,590,9937,14]
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
    parser.add_argument("--model", "-m",  default="cmw")
    parser.add_argument( "-k",  action='store_true')
    parser.add_argument( "-s",  action='store_true')
    parser.add_argument("--times")
    

    args = parser.parse_args()
    if args.k:
        residual_graph(args.filenames)
    if args.s:
        super_graph(args.filenames)
    model = []
    if args.model == "cm0":
        model = [0,0,0,0,0]
    elif args.model == "cmc":
        model = [1,1,1,1,1]
    elif args.model == "cmw":
        model = [211,34,590,9937,14]
    else:
        model = [int(num) for num in args.model.split(",")]

    if args.times:
        average_times = {filename:float(time) for time, filename in izip(args.times.split(), args.filenames)}
    else:
        average_times = trace_parser.calculate_average_times()
    programs = trace_parser.parse_files(args.filenames)
    counts = {program.name: program.class_counts() for program in programs}
    
    trace_utils.Fragment.model = model
    costs = [dot(counts[program.name], model) for program in programs]
    if model == [0,0,0,0,0]:
        print "FOOOOOO"
        costs = [program.cost() for program in programs]
    times = [average_times[program.name] for program in programs]
    for cost in costs:
        print cost
    names = [program.name for program in programs]
    graph(costs, times, names, args.model)
    #produce_gnuplot_file(costs, times,names)
    

    
if __name__ == '__main__':
    main()
