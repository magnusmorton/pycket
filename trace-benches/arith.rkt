#lang racket/base


(define SIZE (string->number (vector-ref (current-command-line-arguments) 0)))
;(define REPS (string->number (vector-ref (current-command-line-arguments) 1)))


(define vec1 (for/vector ([i (in-range SIZE)])
               (random 100)))

(define out (make-vector SIZE 0))

(require (for-syntax racket/syntax))
(require (for-syntax racket/base))

(define-for-syntax ops '(+ - * /))
(define-syntax (test stx)
  (syntax-case stx ()
    [( _ type )
     #`(time (for ([i  vec1])
               (let* (
                      #,@(for/list ([x (in-range 10)])
                           (if (equal? x 0)
                               #`[#,(string->symbol (format "binding~a" x)) i]
                               #`[#,(string->symbol (format "binding~a" x)) (#,(list-ref ops (random 3)) #,(string->symbol (format "binding~a" (random x))) #,(random 100))])))
               (vector-set! out i binding9))))]))



(test "foo")
(write out)
