import argparse
import sys
from itertools import izip
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np
import trace_parser
import trace as trace_utils

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
    rects0 = plt.bar(ind, res0, width, color='r')
    rectsc = plt.bar(ind+width, resc, width, color='g')
    rectsw = plt.bar(ind+ 2*width, resw, width, color='b')
    plt.ylabel("residual")
    plt.title("Residuals for each benchmark")
    plt.xticks(ind + 1.5*width, names, rotation=30, ha = 'right')
    plt.legend((rects0[0], rectsc[0], rectsw[0]), ("CM0", "CMC", "CMW"), title="Cost Model")
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
    coeffs = np.polyfit(costs, times, 1)
    fit_fn = np.poly1d(coeffs)
    print fit_fn
    print rsquared(coeffs, costs, times)
    plt.plot( costs, times,  'xg' , costs, fit_fn(costs), '-b')
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
    graph(costs, times, names, args.model)
    #produce_gnuplot_file(costs, times,names)
    

    
if __name__ == '__main__':
    main()
