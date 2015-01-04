from pycket.analysis.base import Analysis

class Simple(Analysis):
    
    def cost(self):
        """ computes the cost of the analysis"""
        return len(self.trace)
