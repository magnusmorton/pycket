# coding: utf-8

def test_string_set_bang(doctest):
    """
    ! (define str (substring "hello world" 0 5))
    ! (string-set! str 0 #\\x)
    > str
    "xello"
    > (immutable? str)
    #f
    """

def test_substring(doctest):
    """
    > (substring "Apple" 1 3)
    "pp"
    > (substring "Apple" 1)
    "pple"
    > (substring "applebee" 5)
    "bee"
    > (substring "applebee" 0 8)
    "applebee"
    """


def test_string_copy_bang(doctest):
    r"""
    > (define s (string #\A #\p #\p #\l #\e))
    > (string-copy! s 4 "y")
    > (string-copy! s 0 s 3 4)
    > s
    "lpply"
    E (let ([s (string #\a #\b #\c)]) (string-copy! s 0 "abde" 0) s)
    """

def test_string_comparison(doctest):
    """
    > (string=? "Apple" "apple")
    #f
    > (string=? "a" "as" "a")
    #f
    > (string<? "Apple" "apple")
    #t
    > (string<? "apple" "Apple")
    #f
    > (string<? "a" "b" "c")
    #t
    > (string<=? "Apple" "apple")
    #t
    > (string<=? "apple" "Apple")
    #f
    > (string<=? "a" "b" "b")
    #t
    > (string>? "Apple" "apple")
    #f
    > (string>? "apple" "Apple")
    #t
    > (string>? "c" "b" "a")
    #t
    > (string>=? "Apple" "apple")
    #f
    > (string>=? "apple" "Apple")
    #t
    > (string>=? "c" "b" "b")
    #t
    > (string-ci=? "Apple" "apple")
    #t
    > (string-ci=? "a" "a" "a")
    #t
    > (string-ci<? "Apple" "apple")
    #f
    > (string-ci<? "apple" "banana")
    #t
    > (string-ci<? "a" "b" "c")
    #t
    > (string-ci<=? "Apple" "apple")
    #t
    > (string-ci<=? "apple" "Apple")
    #t
    > (string-ci<=? "a" "b" "b")
    #t
    > (string-ci>? "Apple" "apple")
    #f
    > (string-ci>? "banana" "Apple")
    #t
    > (string-ci>? "c" "b" "a")
    #t
    > (string-ci>=? "Apple" "apple")
    #t
    > (string-ci>=? "apple" "Apple")
    #t
    > (string-ci>=? "c" "b" "b")
    #t
    """

def test_bytes_comparison(doctest):
    """
    > (bytes=? #"Apple" #"apple")
    #f
    > (bytes=? #"a" #"as" #"a")
    #f
    > (bytes<? #"Apple" #"apple")
    #t
    > (bytes<? #"apple" #"Apple")
    #f
    > (bytes<? #"a" #"b" #"c")
    #t
    > (bytes>? #"Apple" #"apple")
    #f
    > (bytes>? #"apple" #"Apple")
    #t
    > (bytes>? #"c" #"b" #"a")
    #t
    """


def test_bytes_append(doctest):
    """
    > (bytes-append #"Apple" #"Banana")
    #"AppleBanana"
    """

def test_string_append(doctest):
    """
    > (string-append "Apple" "Banana")
    "AppleBanana"
    """

def test_bytes_to_string_utf8(doctest):
    """
    > (bytes->string/utf-8 (bytes 65 66 67))
    "ABC"
    """

def test_string_ref(doctest):
    r"""
    > (string-ref "abcdef" 0)
    #\a
    > (string-ref "abcdef" 1)
    #\b
    > (string-ref "abcdef" 2)
    #\c
    > (string-ref "abcdef" 3)
    #\d
    > (string-ref "abcdef" 4)
    #\e
    > (string-ref "abcdef" 5)
    #\f
    E (string-ref "abcdef" 6)
    E (string-ref "abcdef" -1)
    """

def test_output_string(doctest):
    r"""
    ! (define p (open-output-string))
    > (write-string "abccarstaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" p 0 10)
    10
    > (get-output-string p)
    "abccarstaa"
    """

def test_immutable_literals(doctest):
    """
    > (immutable? "abc")
    #t
    """

def test_string_to_immutable(doctest):
    r"""
    > (string->immutable-string "abc") ; easy case
    "abc"
    > (string->immutable-string (string #\a #\b))
    "ab"
    > (immutable?  (string #\a #\b))
    #f
    > (immutable? (string->immutable-string (string #\a #\b)))
    #t
    """

def test_string_to_symbol(doctest):
    """
    > (string->symbol "abc")
    'abc
    > (symbol->string 'abc)
    "abc"
    > (symbol->string (string->unreadable-symbol "abc"))
    "abc"
    > (symbol->string (string->uninterned-symbol "abc"))
    "abc"
    > (eq? (string->unreadable-symbol "abc") (string->unreadable-symbol "abc"))
    #t
    > (eq? (string->symbol "abc") (string->symbol "abc"))
    #t
    > (eq? (string->symbol "abc") 'abc)
    #t
    > (eq? (string->unreadable-symbol "abc") 'abc)
    #f
    > (eq? (string->uninterned-symbol "abc") (string->uninterned-symbol "abc"))
    #f
    """

def test_char_integer(doctest):
    """
    > (char->integer (integer->char 65))
    65
    """

def test_string_change_case(doctest):
    """
    > (string-upcase "abc")
    "ABC"
    > (string-upcase "abc__123")
    "ABC__123"
    """


def test_unicode(doctest):
    u"""
    ! (define str (substring "hello world" 0 5))
    ! (define str1 (substring "hello fuß" 0 5))
    ! (string-set! str 1 #\\ä)
    ! (string-set! str1 1 #\\ä)
    > str
    "hällo"
    > str1
    "hällo"
    > (immutable? str)
    #f
    """
