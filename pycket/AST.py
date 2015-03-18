from rpython.rlib import jit

class AST(object):
    _attrs_ = ["should_enter", "mvars", "surrounding_lambda", "_stringrepr", "app_like", "count", "the_lam", "in_cycle", "is_bad"]
    _immutable_fields_ = ["should_enter", "surrounding_lambda", "app_like"]
    _settled_ = True

    should_enter = False # default value
    _stringrepr = None # default value
    mvars = None
    surrounding_lambda = None
    app_like = False

    simple = False

    is_label = False

    in_cycle = False

    the_lam = None

    is_bad = False

    count = 0

    def defined_vars(self): return {}

    def interpret(self, env, cont):
        from pycket.interpreter import return_value_direct
        # default implementation for simple AST forms
        assert self.simple
        # interpret should only be called from interpret_one, therefore it's
        # safe to not use the Label implementation of return_value here
        return return_value_direct(self.interpret_simple(env), env, cont)

    def interpret_simple(self, env):
        raise NotImplementedError("abstract base class")

    def set_surrounding_lambda(self, lam):
        from pycket.interpreter import Lambda
        assert isinstance(lam, Lambda)
        self.surrounding_lambda = lam
        for child in self.direct_children():
            child.set_surrounding_lambda(lam)

    def set_should_enter(self):
        """ Set the should_enter field and returns whether or not the field was
        already set. This looks potentially dangerous: the field is marked
        immutable above. It works however, because should_enter MUST only be
        used for deciding whether to use can_enter_jit or not. As long as that
        is the case, mutating it without informing the JIT is fine: We don't
        want the existing JIT code to be thrown out just because we set a flag
        on an AST somewhere that was already traced. The interpreter is not
        affected and will see the change, thus potentially newly tracing the
        AST.
        """
        if not self.should_enter:
            self.should_enter = True
            return True
        return False

    def direct_children(self):
        return []

    def free_vars(self):
        free_vars = {}
        for child in self.direct_children():
            free_vars.update(child.free_vars())
        return free_vars

    def assign_convert(self, vars, env_structure):
        """ make a copy of the AST that converts all writable variables into
        using cells. In addition, compute the state of the environment for
        every AST node that needs to know.

        The vars argument contains the variables that need to use cells.
        The env_structure is an instance of SymList (or None) describing the
        environment at that AST node.
        """
        raise NotImplementedError("abstract base class")

    def mutated_vars(self):
        if self.mvars is not None:
            return self.mvars
        self.mvars = self._mutated_vars()
        return self.mvars

    def _mutated_vars(self):
        raise NotImplementedError("abstract base class")

    def tostring(self):
        _stringrepr = self._stringrepr
        if _stringrepr is None:
            _stringrepr = self._stringrepr = self._tostring()
        return _stringrepr

    def _tostring(self):
        return "UNKNOWN AST: "

    def __str__(self):
        return self.tostring()

