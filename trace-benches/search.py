import argparse
import copy
import numpy as np
import time
import random
import signal
import sys
from itertools import izip

from scipy import stats

import trace as trace_utils
import trace_parser

dot = lambda x,y: sum(a*b for a,b in izip(x,y))

MAX = 10000
def half_add(a, b, cap):
    s = a + b
    r = s - cap
    c = 0
    if r >= 0:
        c = 1
        s = r
    return (s, c)

def full_add(a, b, cap, step):
    pairs = zip(a,b)
    pairs.reverse()
    result = []
    carry = 0
    for pair in pairs:
        res = half_add(pair[0], pair[1] + carry, cap)
        result.append(res[0])
        carry = res[1] * step
    result.reverse()
    return result
        

def models(start, end, cap, step):
    current = list(start)
    while current != end:
        current = full_add(current, step, cap, step[-1])
        yield current

        
def fit(costs, times):
    # import pdb
    # pdb.set_trace()
    x = np.array(costs)
    y = np.array(times)
    _,_,r,_,_ = stats.linregress(x,y)
    return r**2


def cross(father, mother):
    child1 = []
    child2 = []
    if random.randint(0,5) == 0:
        for i in xrange(len(father.model)):
            if random.getrandbits(1):
                child1.append(father.model[i])
                child2.append(mother.model[i])
            else:
                child1.append(mother.model[i])
                child2.append(father.model[i])
    else:
        return  father,mother
    return Solution(child1),Solution(child2)

def evaluate(population, programs,counts,  times):
    fitnesses = []
    for model in population:
        costs = [dot(counts[program.name], model) for program in programs]
        fitnesses.append(costs, times)
    return fitnesses
        
        


def initialize(size):
    population = []
    for _ in xrange(size):
        population.append(Solution(random.sample(xrange(MAX), 5)))
    return population


class Solution(object):
    times = None
    counts = None
    programs = None
    def __init__(self, model):
        self.model = model
        self._fitness = None
        

    def fitness(self):
        if self._fitness:
            return self._fitness
        if not (Solution.times and Solution.counts):
            raise Exception("No times or counts")
        costs = [dot(Solution.counts[program.name], self.model) for program in Solution.programs]
        self._fitness = fit(costs, Solution.times)
        return self._fitness

    def mutate(self):
        for i in xrange(len(self.model)):
            if random.randint(0,50) == 0:
                self.model[i] = random.randint(0,MAX)
        self._fitness = None
        return self

    def __str__(self):
        return str(self.model)

        
def selection(population):
    one = random.choice(population)
    two = random.choice(population)
    return fittest(one,two)

def fittest(a,b):
    if a.fitness() > b.fitness():
        return a
    else:
        return b
    
def ga_search(programs,average_times, counts):
    Solution.programs = programs
    Solution.counts = counts
    times = [average_times[program.name] for program in programs]
    Solution.times = times
    SIZE = 30
    generations = 30000
    population  = initialize(SIZE)
    initial = copy.deepcopy(population)
    max_key = lambda a: a.fitness()
    best_rsq = 0
    best = None
    for i in xrange(generations):
        if i % 100 == 0:
            print "generation:", i
            for solution in population:
                print solution
        new_pop = []
        elite = max(population, key=max_key)
        if not best:
            best = elite
        elif elite.fitness() > best.fitness():
            best = elite
        new_pop.append(elite)
        while len(new_pop) < SIZE:
            father = selection(population)
            mother = selection(population)
            new_pop.extend(cross(father,mother))
        population = [solution.mutate() for solution in new_pop]
    elite = max(population, key=max_key)
    if not best:
        best = elite
    elif elite.fitness() > best.fitness():
        best = elite
    print "Elite:", elite.model, elite.fitness()
    print "Best:", best.model, best.fitness()
    print "INITIAL:"
    for solution in initial:
        print solution
            
            

def main():
    parser = argparse.ArgumentParser(description="Run cost analysis")
    parser.add_argument("filenames", metavar="<file>", nargs = '+')
    parser.add_argument("--start", "-s",  default="0,0,0,0,0")
    parser.add_argument("--end", "-e",  default="10,10,10,10,10")
    parser.add_argument("--cap", "-c", default=11, type=int)
    parser.add_argument("--step", "-t", default=1, type=int)
    parser.add_argument("-g",action='store_true')
    
    args = parser.parse_args()
    start = [int(num) for num in args.start.split(",")]
    end = [int(num) for num in args.end.split(",")]
    step = [0,0,0,0,args.step]
    average_times = trace_parser.calculate_average_times()
    programs = trace_parser.parse_files(args.filenames)
    counts = {program.name: program.class_counts() for program in programs}
    if args.g:
        return ga_search(programs, average_times, counts)
    best = None
    def handler(s, frame):
        print "Terminated... Current best:", best
        sys.exit(0)
    signal.signal(signal.SIGINT, handler)
    print "Beginning search...."
    then = time.clock()
    for model in models(start,end,args.cap, step):
        trace_utils.Fragment.model = model
        costs = [dot(counts[program.name], model) for program in programs]
        times = [average_times[program.name] for program in programs]
        rsq = fit(costs, times)
        if not best:
            best = (model, rsq)
        elif rsq > best[1]:
            best = (model, rsq)
    now = time.clock()

    print "Time:", now - then
    print "Best:", best


if __name__ == '__main__':
    main()

    



# max_len = 0
# longest = None
# for val in values:
#     if len(val) > max_len:
#         max_len = len(val)
#         longest = val

# zero_longest = {key:0 for key in longest}
# values = [dict(zero_longest.items() + val.items()) for val in values]

# # need values in key order
# coeffs = [[value for (key, value) in sorted(eqn.items())] for eqn in values]    

# a = np.array(coeffs)
# b = np.array(times)



# savemat("results.mat", {"counts":a, "times":b})
# # we are probably overconstrained
# x = nnls(a, b)
                
# sorted_costs = [value for (key, value) in sorted(costs.items())]



