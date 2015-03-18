from pycket.error             import SchemeException
from rpython.tool.pairtype    import extendabletype
from rpython.rlib import jit, objectmodel

class W_ProtoObject(object):
    """ abstract base class of both actual values (W_Objects) and multiple
    return values (Values)"""
    _attrs_ = []
    _settled_ = True

    def as_real_value(self):
        raise NotImplementedError("not a real value!")

    def num_values(val):
        raise NotImplementedError("not a real value!")

    def get_value(val, index):
        raise NotImplementedError("not a real value!")

    def get_all_values(self):
        raise NotImplementedError("not a real value!")

class W_Object(W_ProtoObject):
    __metaclass__ = extendabletype
    _attrs_ = []
    errorname = "%%%%unreachable%%%%"
    def __init__(self):
        raise NotImplementedError("abstract base class")

    def num_values(self):
        return 1

    def get_value(self, index):
        assert index == 0
        return self

    def get_all_values(self):
        return [self]

    def iscallable(self):
        return False

    def call(self, args, env, cont):
        raise SchemeException("%s is not callable" % self.tostring())

    def call_with_extra_info(self, args, env, cont, calling_app):
        return self.call(args, env, cont)

    def enable_jitting(self):
        pass # need to override in callables that are based on an AST

    # an arity is a pair of a list of numbers and either -1 or a non-negative integer
    def get_arity(self):
        from pycket.interpreter import Arity
        if self.iscallable():
            return Arity.unknown
        else:
            raise SchemeException("%s does not have arity" % self.tostring())

    def is_proper_list(self):
        return False

    def is_impersonator(self):
        return self.is_chaperone()
    def is_chaperone(self):
        return False
    def is_proxy(self):
        return self.is_chaperone() or self.is_impersonator()
    def get_proxied(self):
        return self
    def get_properties(self):
        return {}
    def is_non_interposing_chaperone(self):
        return False

    def immutable(self):
        return False

    def equal(self, other):
        return self is other # default implementation

    def eqv(self, other):
        return self is other # default implementation

    def hash_equal(self):
        return objectmodel.compute_hash(self) # default implementation
    hash_eqv = hash_equal

    def tostring(self):
        return str(self)

    # for expose
    @classmethod
    def make_unwrapper(cls):
        if cls is W_Object:
            return lambda x: x, ''
        def unwrap(w_object):
            if isinstance(w_object, cls):
                return w_object
            return None
        return unwrap, cls.errorname

class SingletonMeta(type):
    def __new__(cls, name, bases, dct):
        result = type.__new__(cls, name, bases, dct)
        result.singleton = result()
        return result

