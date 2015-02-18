#lang pycket #:stdlib

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))

(define enumFromTo
  (lambda (m n)
    (if (> m n) '() (cons m (enumFromTo (+ m 1) n)))))

(define sum
  (lambda (_list)
    (foldl (lambda (s x) (+ s x)) 0 _list)))



(time  (enumFromTo 1 SIZE))

