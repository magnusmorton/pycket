#lang racket/base

(require racket/stream)

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0)))
(define REPS (string->number (vector-ref (current-command-line-arguments) 1)))


;; inputs; SIZE should be <= 2 * 10^6 to make sure we don't exceed word size
(define vec1 (make-vector (+ 3 SIZE) 3))
(define vec2 (in-range 5 (+ 5 SIZE)))

(define (dot u v) (for/sum ([x u] [y v]) (* x y)))
(require (for-syntax racket/syntax))
(require (for-syntax racket/base))
(define-syntax (looper stx)
  (syntax-case stx ()
    [( _ type )
     #`(time (for ([i (in-range REPS)])
          (begin
            #,@(for/list ([x (in-range Z)])
                 #'(vector-set! vec1 i (* 123.34 1234))))))
     ]
  ))

(looper "foo"  )
