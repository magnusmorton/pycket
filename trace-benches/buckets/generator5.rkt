#lang racket/base

(require racket/stream)

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0)))
(define REPS (string->number (vector-ref (current-command-line-arguments) 1)))



;; inputs; SIZE should be <= 2 * 10^6 to make sure we don't exceed word size
(define vec1 (make-vector (+ 3 SIZE) 3))
(define vec2 (in-range 5 (+ 5 SIZE)))
(define out (make-vector SIZE 0))
(define s "abcdef")

(define b #f)
(define l '())
(define (dot u v) (for/sum ([x u] [y v]) (* x y)))
(require (for-syntax racket/syntax))
(require (for-syntax racket/base))
(define-for-syntax ops '(+ - * /))
(define-syntax (looper stx)
  (syntax-case stx ()
    [( _ type  )
     #`(time (for ([i (in-range REPS)])
               (begin
                 #,@(for/list ([x (in-range  200)])
                      (case (modulo x 37)
                        [(in-range 10 )#`(vector-set! vec1 i (* 123.34 #,(random 10)) )]
                        [(in-range 10 15 ) #`(let* (
                                              #,@(for/list ([y (in-range 10)])
                                                   (if (equal? y 0)
                                                       #`[#,(string->symbol (format "binding~a" y)) i]
                                                       #`[#,(string->symbol (format "binding~a" y)) (#,(list-ref ops (random 3)) #,(string->symbol (format "binding~a" (random y))) #,(random 100))])))
                                         (vector-set! out i binding9))]
                        [(in-range 15 30) #'(set! l (cons l "foo"))]
                        [else #`(set! b (< 50 #,(random 100)))])))))]))



(looper "foo" )
