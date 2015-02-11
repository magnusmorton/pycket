from pycket.analysis.base import Analysis

class Simple(Analysis):
    
    def cost(self, trace):
        """ computes the cost of the analysis"""
        count  = 0
        for instruction in trace:
            """TODO: test this"""
            if instruction.getopname() != "debug_merge_point":
                count += 1
        return count
