import argparse
import numpy as np
import matplotlib.pyplot as plt
from itertools import izip

parser = argparse.ArgumentParser(description="plot single trace")
parser.add_argument("filenames", metavar="<file>")
parser.add_argument("--title", "-t",  default="")
args = parser.parse_args()

def k_stats(costs, times):
    ks = np.array([time/cost for cost, time in izip(costs, times)])
    print "Mean: " + str(np.mean(ks)) + " STD DEV: " + str(np.std(ks))
    
costs = []
times = []
with open(args.filenames, 'r') as f:
    for line in f:
        split = line.split()
        times.append(float(split[0]))
        costs.append(int(split[1]))


coeffs = np.polyfit(costs, times, 1)
fit_fn = np.poly1d(coeffs)
k_stats(costs, times)
print fit_fn
print "rsquared"
plt.ylabel("Execution time ($\mu s$)")
plt.xlabel("Cost")
plt.title(args.title)
plt.plot( costs, times,  'xg' , costs, fit_fn(costs), '-b')
plt.show()
