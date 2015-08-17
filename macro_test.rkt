#lang racket/base


(define SIZE 10000)
(define REPS 10000)

(define vec1 (make-vector (+ 3 SIZE) 3))

(require (for-syntax racket/syntax))
(require (for-syntax racket/base))
(define-syntax (looper stx)
  (syntax-case stx ()
    [( _ type  )
     #`(for ([i (in-range REPS)])
               (begin
                 #,@(for/list ([x (in-range  1491)])
                      #`(vector-set! vec1 i (* 123.34 #,(random 10))))))]))


(syntax->datum (expand-once #'(looper "foo")))
