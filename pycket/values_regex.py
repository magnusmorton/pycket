from pycket.base import W_Object
from pycket.error import SchemeException
from pycket import values, values_string
from pycket import regexp

from rpython.rlib.rsre import rsre_core, rsre_char
from rpython.rlib import buffer, jit

CACHE = regexp.RegexpCache()

class PortBuffer(buffer.Buffer):
    """match context for matching in a port."""
    # XXX how to extend to unicode?

    _immutable_ = True

    def __init__(self, w_port):
        self.w_port = w_port
        l = w_port._length_up_to_end()
        assert l >= 0
        self.length = l
        self.read_so_far = []

    def getlength(self):
        return self.length

    def getitem(self, index):
        if index >= len(self.read_so_far):
            nchars = len(self.read_so_far) - index + 1
            self.read_so_far.extend(list(self.w_port.read(nchars)))
        ch = self.read_so_far[index]
        return ch


class W_AnyRegexp(W_Object):
    _immutable_fields_ = ["source"]
    errorname = "regexp"
    def __init__(self, source):
        self.source = source
        self.code = None

    def ensure_compiled(self):
        if self.code is None:
            code, flags, groupcount, groupindex, indexgroup, group_offsets = regexp.compile(CACHE, self.source, 0)
            self.code = code
            self.flags = flags
            self.groupcount = groupcount
            self.groupindex = groupindex
            self.indexgroup = indexgroup
            self.group_offsets = group_offsets

    def match_string(self, s):
        self.ensure_compiled()
        ctx = rsre_core.search(self.code, s)
        if not ctx:
            return None
        return _extract_result(ctx, self.groupcount)

    def match_string_positions(self, s):
        self.ensure_compiled()
        ctx = rsre_core.search(self.code, s)
        if ctx is None:
            return []
        return _extract_spans(ctx, self.groupcount)

    def match_port_positions(self, w_port):
        raise NotImplementedError("match_port_position: not yet implemented")

    def match_port(self, w_port):
        self.ensure_compiled()
        if isinstance(w_port, values.W_StringInputPort):
            # fast path
            ctx = rsre_core.search(self.code, w_port.str, start=w_port.ptr)
            if not ctx:
                return None
            start, end = ctx.span(0) # the whole match
            w_port.ptr = end
            return _extract_result(ctx, self.groupcount)
        buf = PortBuffer(w_port)
        ctx = rsre_core.BufMatchContext(self.code, buf, 0, buf.getlength(), 0)
        matched = rsre_core.search_context(ctx)
        if not matched:
            return None
        return _extract_result(ctx, self.groupcount)

    def equal(self, other):
        if not isinstance(other, W_AnyRegexp):
            return False
        if type(self) is type(other):
            return self.source == other.source
        return False

@rsre_core.specializectx
@jit.unroll_safe
def _extract_spans(ctx, groupcount):
    return [ctx.span(i) for i in range(groupcount + 1)]

@rsre_core.specializectx
@jit.unroll_safe
def _extract_result(ctx, groupcount):
    result = []
    for i in range(groupcount + 1):
        start, end = ctx.span(i)
        if start == -1 and end == -1:
            result.append(None)
        else:
            assert 0 <= start
            assert 0 <= end
            result.append(_getslice(ctx, start, end))
    return result

@rsre_core.specializectx
def _getslice(ctx, start, end):
    if isinstance(ctx, rsre_core.StrMatchContext):
        return ctx._string[start:end]
    else:
        return ''.join([chr(ctx.str(j)) for j in range(start, end)])

class W_Regexp(W_AnyRegexp): pass
class W_PRegexp(W_AnyRegexp): pass
class W_ByteRegexp(W_AnyRegexp): pass
class W_BytePRegexp(W_AnyRegexp): pass

