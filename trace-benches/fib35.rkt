#lang pycket

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Fibonacci function

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))

(define fib
  (lambda (n)
    (if (< 1 n) (+ (fib (- n 1)) (fib (- n 2))) 1)))

;; timed call
(printf "(fib 35)\n")
(time (printf "~a\n" (fib SIZE)))
