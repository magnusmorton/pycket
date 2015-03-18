from rpython.rlib import jit

# TODO: Find heavily executed lambdas that do not participate in a loop in the
# callgraph.

class CallGraph(object):
    def __init__(self):
        self.calls     = {}
        self.recursive = {}

    def register_call(self, lam, calling_app, cont, env):
        if jit.we_are_jitted():
            return
        if not calling_app:
            return
        calling_lam = calling_app.surrounding_lambda
        if not calling_lam:
            return
        subdct = self.calls.get(calling_lam, None)
        if subdct is None:
            self.calls[calling_lam] = subdct = {}
            lam_in_subdct = False
        else:
            lam_in_subdct = lam in subdct
        cont_ast = cont.get_next_executed_ast()
        config = env.pycketconfig()
        is_recursive = False
        if not lam_in_subdct:
            subdct[lam] = None
            if self.is_recursive(calling_lam, lam):
                is_recursive = True
                if config.log_callgraph:
                    print "enabling jitting", calling_lam.tostring()
                calling_lam.enable_jitting()
        # It is possible to have multiple consuming continuations for a given
        # function body. This will attempt to mark them all.
        same_lambda = cont_ast and cont_ast.surrounding_lambda is calling_lam
        if same_lambda:
            if lam_in_subdct: # did not call is_recursive yet
                is_recursive = self.is_recursive(calling_lam, lam)
            if is_recursive:
                if cont_ast.set_should_enter() and config.log_callgraph:
                    print "jitting downrecursion", cont_ast.tostring()

    def is_recursive(self, lam, starting_from=None):
        # quatratic in theory, hopefully not very bad in practice
        if lam in self.recursive:
            lam.set_in_cycle()
            return True
        if starting_from is None:
            starting_from = lam
        reachable = self.calls.get(starting_from, None)
        if reachable is None:
            return False
        todo = []
        for key in reachable:
            todo.append((key, Path(starting_from, None)))
        visited = {}
        while todo:
            current, path = todo.pop()
            if current is lam:
                lam.set_in_cycle()
                self.recursive[lam] = None
                # all the lambdas in the path are recursive too
                while path:
                    path.node.set_in_cycle()
                    self.recursive[path.node] = None
                    path = path.prev
                return True
            if current in visited:
                continue
            reachable = self.calls.get(current, None)
            if reachable:
                for key in reachable:
                    todo.append((key, Path(current, path)))
            visited[current] = None
        return False

class Path(object):
    def __init__(self, node, prev):
        self.node = node
        self.prev = prev

    def __repr__(self):
        return "%s -> %s" % (self.node, self.prev)
