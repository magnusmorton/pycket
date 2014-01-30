
import pytest
from pycket.json import loads

def _compare(string, expected):
    json = loads(string)
    assert json._unpack_deep() == expected

def test_simple():
    _compare("1", 1)
    _compare("\"abc\"", "abc")
    _compare("1.2", 1.2)

def test_array():
    _compare("[]", [])
    _compare("[1]", [1])
    _compare("[1, 2.0, 3.0, \"abc\", [10.0, \"def\"]]", [1, 2.0, 3.0, "abc", [10.0, "def"]])

def test_object():
    _compare("{}", {})
    _compare("{\"a\": 1}", {"a": 1})
    _compare("{\"a\": 1, \"123\": \"ab\", \"subobj\": {\"d\": 12.0}, \"subarr\": [1]}", {"a": 1, "123": "ab", "subobj": {"d": 12.0}, "subarr": [1]})

def test_escaped_string():
    _compare('"\\n"', "\n")
    _compare('"\\n\\t\\b\\f\\r\\\\"', "\n\t\b\f\r\\")
    _compare('"\\n\\t\\b\\f\\r\\\\"', "\n\t\b\f\r\\")
    _compare('"\\""', '"')

def test_tostring_string_escaping():
    json = loads('"\\n"')
    assert json.tostring() == '"\\n"'