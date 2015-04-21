#lang racket/base

(define out null)

(define (test)
  (for ([i (in-range 1000)])
    (let* ([x (random 100)]
           [y (+ 3 x)]
           [z (* y x)]
           [a (+ z y)])
      (set! out a))))


(begin
  (test)
  (write out))
