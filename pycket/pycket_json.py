from rpython.rlib.rstring import StringBuilder
from rpython.rlib.runicode import unicode_encode_utf_8
from rpython.rlib.objectmodel import specialize
from rpython.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from rpython.rlib.parsing.tree import Symbol, Nonterminal, RPythonVisitor
from rpython.tool.pairtype import extendabletype

# Union-Object to represent a json structure in a static way
class JsonBase(object):
    __metaclass__ = extendabletype

    is_string = is_int = is_float = is_bool = is_object = is_array = is_null = False

    def __init__(self):
        raise NotImplementedError("abstract base class")

    def tostring(self):
        raise NotImplementedError("abstract base class")

    def is_primitive(self):
        return False

    def _unpack_deep(self):
        "NON_RPYTHON"

    def value_array(self):
        raise TypeError

    def value_object(self):
        raise TypeError

    def value_string(self):
        raise TypeError

    def value_float(self):
        raise TypeError

    def value_int(self):
        raise TypeError


class JsonPrimitive(JsonBase):
    def __init__(self):
        pass

    def is_primitive(self):
        return True

class JsonNull(JsonPrimitive):
    is_null = True

    def tostring(self):
        return "null"

    def _unpack_deep(self):
        return None

class JsonFalse(JsonPrimitive):
    is_bool = True

    def tostring(self):
        return "false"

    def _unpack_deep(self):
        return False


class JsonTrue(JsonPrimitive):
    is_bool = True

    def tostring(self):
        return "true"

    def _unpack_deep(self):
        return True

class JsonInt(JsonPrimitive):
    is_int = True

    def __init__(self, value):
        self.value = value

    def tostring(self):
        return str(self.value)

    def _unpack_deep(self):
        return self.value

    def value_int(self):
        return self.value

class JsonFloat(JsonPrimitive):
    is_float = True

    def __init__(self, value):
        self.value = value

    def tostring(self):
        return str(self.value)

    def value_float(self):
        return self.value

    def _unpack_deep(self):
        return self.value

class JsonString(JsonPrimitive):
    is_string = True

    def __init__(self, value):
        assert value is not None
        self.value = value

    def tostring(self):
        # this function should really live in a slightly more accessible place
        from pypy.objspace.std.bytesobject import string_escape_encode
        return string_escape_encode(self.value, '"')

    def _unpack_deep(self):
        return self.value

    def value_string(self):
        return self.value

class JsonObject(JsonBase):
    is_object = True

    def __init__(self, dct):
        self.value = dct

    def tostring(self):
        return "{%s}" % ", ".join(["\"%s\": %s" % (key, self.value[key].tostring()) for key in self.value])

    def _unpack_deep(self):
        result = {}
        for key, value in self.value.iteritems():
            result[key] = value._unpack_deep()
        return result

    def value_object(self):
        return self.value

class JsonArray(JsonBase):
    is_array = True

    def __init__(self, lst):
        self.value = lst

    def tostring(self):
        return "[%s]" % ", ".join([e.tostring() for e in self.value])

    def _unpack_deep(self):
        return [e._unpack_deep() for e in self.value]

    def value_array(self):
        return self.value

json_null = JsonNull()

json_true = JsonTrue()

json_false = JsonFalse()


class FakeSpace(object):

    w_None = json_null
    w_True = json_true
    w_False = json_false
    w_ValueError = ValueError
    w_UnicodeDecodeError = UnicodeDecodeError
    w_UnicodeEncodeError = UnicodeEncodeError
    w_int = JsonInt
    w_float = JsonFloat

    def newtuple(self, items):
        return None

    def newdict(self):
        return JsonObject({})

    def newlist(self, items):
        return JsonArray([])

    def newint(self, intval):
        return JsonInt(intval)

    def newfloat(self, floatval):
        return JsonFloat(floatval)

    def newunicode(self, unicodeval):
        return JsonString(unicodeval.encode('utf-8'))

    def newtext(self, text):
        return JsonString(text)

    def newbytes(self, bytes):
        return JsonString(bytes)

    def call_method(self, obj, name, arg):
        assert name == 'append'
        assert isinstance(obj, JsonArray)
        obj.value.append(arg)
    call_method._dont_inline_ = True

    def call_function(self, w_func, *args_w):
        assert 0

    def setitem(self, d, key, value):
        assert isinstance(d, JsonObject)
        assert isinstance(key, JsonString)
        d.value[key.value_string()] = value

    def wrapunicode(self, x):
        return JsonString(unicode_encode_utf_8(x, len(x), "strict"))

    def wrapint(self, x):
        return JsonInt(x)

    def wrapfloat(self, x):
        return JsonFloat(x)

    def wrap(self, x):
        if isinstance(x, int):
            return JsonInt(x)
        elif isinstance(x, float):
            return JsonFloat(x)
        return self.wrapunicode(unicode(x))
    wrap._annspecialcase_ = "specialize:argtype(1)"

fakespace = FakeSpace()

from pypy.module._pypyjson.interp_decoder import JSONDecoder

class OwnJSONDecoder(JSONDecoder):
    def __init__(self, s):
        self.space = fakespace
        self.s = s
        # we put our string in a raw buffer so:
        # 1) we automatically get the '\0' sentinel at the end of the string,
        #    which means that we never have to check for the "end of string"
        self.ll_chars = s + chr(0)
        self.pos = 0
        self.last_type = 0

    def close(self):
        pass

    @specialize.arg(1)
    def _raise(self, msg, *args):
        raise ValueError(msg % args)

    def decode_float(self, i):
        start = i
        while self.ll_chars[i] in "+-0123456789.eE":
            i += 1
        self.pos = i
        return self.space.wrap(float(self.getslice(start, i)))

    def decode_string(self, i):
        start = i
        while True:
            # this loop is a fast path for strings which do not contain escape
            # characters
            ch = self.ll_chars[i]
            i += 1
            if ch == '"':
                content_utf8 = self.getslice(start, i-1)
                self.last_type = 1
                self.pos = i
                return JsonString(content_utf8)
            elif ch == '\\':
                self.pos = i-1
                return self.decode_string_escaped(start)
            elif ch < '\x20':
                self._raise("Invalid control character at char %d", self.pos-1)



def loads(s):
    decoder = OwnJSONDecoder(s)
    try:
        w_res = decoder.decode_any(0)
        i = decoder.skip_whitespace(decoder.pos)
        if i < len(s):
            start = i
            end = len(s) - 1
            raise ValueError("Extra data: char %d - %d" % (start, end))
        return w_res
    finally:
        decoder.close()

