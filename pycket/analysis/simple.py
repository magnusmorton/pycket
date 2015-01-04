from pycket.analysis.base import Analysis

class Simple(Analysis):
    
    def __init__(self):
        super(Simple, self).__init__()
        self.trace = None

    def cost(self):
        """ computes the cost of the analysis"""
        return self.trace
