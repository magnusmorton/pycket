
from pycket.values import W_MVector, W_VectorSuper, W_Fixnum, W_Flonum, W_Character, UNROLLING_CUTOFF
from pycket.base import W_Object, SingletonMeta
from pycket import config

from rpython.rlib import rerased
from rpython.rlib.objectmodel import newlist_hint, import_from_mixin
from rpython.rlib import debug, jit


@jit.look_inside_iff(lambda elements, immutable:
        jit.loop_unrolling_heuristic(
                elements, len(elements), UNROLLING_CUTOFF))
def _find_strategy_class(elements, immutable):
    if not config.strategies or len(elements) == 0:
        # An empty vector stays empty forever. Don't implement special EmptyVectorStrategy.
        return ObjectVectorStrategy.singleton
    single_class = type(elements[0])
    for elem in elements:
        if not isinstance(elem, single_class):
            if immutable:
                return ObjectImmutableVectorStrategy.singleton
            return ObjectVectorStrategy.singleton
    if single_class is W_Fixnum:
        if immutable:
            return FixnumImmutableVectorStrategy.singleton
        return FixnumVectorStrategy.singleton
    if single_class is W_Flonum:
        if immutable:
            return FlonumImmutableVectorStrategy.singleton
        return FlonumVectorStrategy.singleton
    if single_class is W_Character:
        if immutable:
            return CharacterImmutableVectorStrategy.singleton
        return CharacterVectorStrategy.singleton
    return ObjectVectorStrategy.singleton


class StrategyVectorMixin(object):
    def get_storage(self):
        return self.storage

    def set_storage(self, storage):
        self.storage = storage

    def ref(self, i):
        return self.get_strategy().ref(self, i)

    def set(self, i, v):
        self.get_strategy().set(self, i, v)

    def immutable(self):
        return self.get_strategy().immutable(self)

    def vector_set(self, i, new, env, cont):
        from pycket.interpreter import return_value
        from pycket.values import w_void
        self.set(i.value, new)
        return return_value(w_void, env, cont)

    def vector_ref(self, i, env, cont):
        from pycket.interpreter import return_value
        return return_value(self.ref(i.value), env, cont)

    # unsafe versions
    def unsafe_ref(self, i):
        return self.get_strategy().ref(self, i, check=False)

    def unsafe_set(self, i, v):
        self.get_strategy().set(self, i, v, check=False)

    def change_strategy(self, new_strategy):
        old_list = self.get_strategy().ref_all(self)
        self.set_strategy(new_strategy)
        self.set_storage(new_strategy.create_storage_for_elements(old_list))


class W_Vector(W_MVector):
    _immutable_fields_ = ["len"]
    errorname = "vector"

    import_from_mixin(StrategyVectorMixin)

    def __init__(self, strategy, storage, len):
        self.strategy = strategy
        self.storage = storage
        self.len = len

    def get_strategy(self):
        return self.strategy

    def set_strategy(self, strategy):
        if not config.strategies:
            assert strategy is ObjectVectorStrategy.singleton
        self.strategy = strategy

    @staticmethod
    def fromelements(elems, immutable=False):
        strategy = _find_strategy_class(elems, immutable)
        storage = strategy.create_storage_for_elements(elems)
        return W_Vector(strategy, storage, len(elems))

    @staticmethod
    def fromelement(elem, times, immutable=False):
        check_list = [elem]
        if times == 0:
            check_list = []
        strategy = _find_strategy_class(check_list, immutable)
        storage = strategy.create_storage_for_element(elem, times)
        return W_Vector(strategy, storage, times)

    def length(self):
        return self.len

    def tostring(self):
        l = self.strategy.ref_all(self)
        return "#(%s)" % " ".join([obj.tostring() for obj in l])

    def equal(self, other):
        # XXX could be optimized using strategies
        if not isinstance(other, W_MVector):
            return False
        if self is other:
            return True
        if self.length() != other.length():
            return False
        for i in range(self.length()):
            if not self.ref(i).equal(other.ref(i)):
                return False
        return True

class W_FlVector(W_VectorSuper):
    _immutable_fields_ = ["len"]
    errorname = "flvector"

    import_from_mixin(StrategyVectorMixin)

    def __init__(self, storage, len):
        self.storage = storage
        self.len = len

    def get_strategy(self):
        return FlonumVectorStrategy.singleton

    def set_strategy(self, strategy):
        assert 0, "unreachable"

    @staticmethod
    def fromelements(elems):
        strategy = FlonumVectorStrategy.singleton
        storage = strategy.create_storage_for_elements(elems)
        return W_FlVector(storage, len(elems))

    @staticmethod
    def fromelement(elem, times):
        check_list = [elem]
        if times == 0:
            check_list = []
        strategy = FlonumVectorStrategy.singleton
        storage = strategy.create_storage_for_element(elem, times)
        return W_FlVector(storage, times)

    def length(self):
        return self.len
    def tostring(self):
        l = self.get_strategy().ref_all(self)
        return "(flvector %s)" % " ".join([obj.tostring() for obj in l])

    def equal(self, other):
        # XXX could be optimized more
        if not isinstance(other, W_FlVector):
            return False
        if self is other:
            return True
        if self.length() != other.length():
            return False
        for i in range(self.length()):
            if not self.ref(i).equal(other.ref(i)):
                return False
        return True

class VectorStrategy(object):
    """ works for any W_VectorSuper that has
    get/set_strategy, get/set_storage
    """
    __metaclass__ = SingletonMeta

    def is_correct_type(self, w_obj):
        raise NotImplementedError("abstract base class")

    def immutable(self, w_vector):
        return False

    def ref(self, w_vector, i, check=True):
        if check:
            self.indexcheck(w_vector, i)
        return self._ref(w_vector, i)
    def set(self, w_vector, i, w_val, check=True):
        if check:
            self.indexcheck(w_vector, i)
        if not self.is_correct_type(w_val):
            self.dehomogenize(w_vector)
            # Now, try again. no need to use the safe version, we already
            # checked the index
            w_vector.unsafe_set(i, w_val)
        else:
            self._set(w_vector, i, w_val)
    def indexcheck(self, w_vector, i):
        assert 0 <= i < w_vector.length()

    def _ref(self, w_vector, i):
        raise NotImplementedError("abstract base class")
    def _set(self, w_vector, i, w_val):
        raise NotImplementedError("abstract base class")
    # def length(self, w_vector):
    #     raise NotImplementedError("abstract base class")
    def ref_all(self, w_vector):
        raise NotImplementedError("abstract base class")

    def create_storage_for_element(self, element, times):
        raise NotImplementedError("abstract base class")
    def create_storage_for_elements(self, elements):
        raise NotImplementedError("abstract base class")


    def dehomogenize(self, w_vector):
        w_vector.change_strategy(ObjectVectorStrategy.singleton)


class ImmutableVectorStrategyMixin(object):
    def immutable(self, w_vector):
        return True

    def _set(self, w_vector, i, w_val):
        assert 0, "unreachable"


class UnwrappedVectorStrategyMixin(object):
    # the concrete class needs to implement:
    # erase, unerase, is_correct_type, wrap, unwrap

    def _storage(self, w_vector):
        l = self.unerase(w_vector.get_storage())
        debug.make_sure_not_resized(l)
        return l

    def _ref(self, w_vector, i):
        assert i >= 0
        return self.wrap(self._storage(w_vector)[i])

    def _set(self, w_vector, i, w_val):
        assert i >= 0
        self._storage(w_vector)[i] = self.unwrap(w_val)

    # def length(self, w_vector):
    #     return len(self._storage(w_vector))

    @jit.look_inside_iff(
        lambda strategy, w_vector: jit.isconstant(w_vector.length()) and
               w_vector.length() < UNROLLING_CUTOFF)
    def ref_all(self, w_vector):
        unwrapped = self._storage(w_vector)
        return [self.wrap(i) for i in unwrapped]

    def create_storage_for_element(self, element, times):
        e = self.unwrap(element)
        return self.erase([e] * times)

    @jit.look_inside_iff(
        lambda self, elements_w:
            jit.loop_unrolling_heuristic(
                    elements_w, len(elements_w), UNROLLING_CUTOFF))
    def create_storage_for_elements(self, elements_w):
        if not elements_w:
            return self.erase([])
        l = [self.unwrap(elements_w[0])] * len(elements_w)
        for i in range(1, len(elements_w)):
            l[i] = self.unwrap(elements_w[i])
        return self.erase(l)


class ObjectVectorStrategy(VectorStrategy):
    import_from_mixin(UnwrappedVectorStrategyMixin)

    erase, unerase = rerased.new_erasing_pair("object-vector-strategry")
    erase = staticmethod(erase)
    unerase = staticmethod(unerase)

    def wrap(self, obj):
        return obj

    def unwrap(self, w_obj):
        return w_obj

    def is_correct_type(self, w_obj):
        return True

    def create_storage_for_elements(self, elements_w):
        return self.erase(elements_w)

    def dehomogenize(self, w_vector):
        assert 0 # should be unreachable because is_correct_type is always True


class ObjectImmutableVectorStrategy(ObjectVectorStrategy):
    import_from_mixin(ImmutableVectorStrategyMixin)

class FixnumVectorStrategy(VectorStrategy):
    import_from_mixin(UnwrappedVectorStrategyMixin)

    erase, unerase = rerased.new_erasing_pair("fixnum-vector-strategy")
    erase = staticmethod(erase)
    unerase = staticmethod(unerase)

    def is_correct_type(self, w_obj):
        return isinstance(w_obj, W_Fixnum)

    def wrap(self, val):
        assert isinstance(val, int)
        return W_Fixnum(val)

    def unwrap(self, w_val):
        assert isinstance(w_val, W_Fixnum)
        return w_val.value

class FixnumImmutableVectorStrategy(FixnumVectorStrategy):
    import_from_mixin(ImmutableVectorStrategyMixin)

class CharacterVectorStrategy(VectorStrategy):
    import_from_mixin(UnwrappedVectorStrategyMixin)

    erase, unerase = rerased.new_erasing_pair("character-vector-strategy")
    erase = staticmethod(erase)
    unerase = staticmethod(unerase)

    def is_correct_type(self, w_obj):
        return isinstance(w_obj, W_Character)

    def wrap(self, val):
        assert isinstance(val, str) and len(val) == 1
        return W_Character(val)

    def unwrap(self, w_val):
        assert isinstance(w_val, W_Character)
        return w_val.value

class CharacterImmutableVectorStrategy(CharacterVectorStrategy):
    import_from_mixin(ImmutableVectorStrategyMixin)

class FlonumVectorStrategy(VectorStrategy):
    import_from_mixin(UnwrappedVectorStrategyMixin)

    erase, unerase = rerased.new_erasing_pair("flonum-vector-strategry")
    erase = staticmethod(erase)
    unerase = staticmethod(unerase)

    def is_correct_type(self, w_obj):
        return isinstance(w_obj, W_Flonum)

    def wrap(self, val):
        assert isinstance(val, float)
        return W_Flonum(val)

    def unwrap(self, w_val):
        assert isinstance(w_val, W_Flonum)
        return w_val.value


class FlonumImmutableVectorStrategy(FlonumVectorStrategy):
    import_from_mixin(ImmutableVectorStrategyMixin)
