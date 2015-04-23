#lang racket/base


(define SIZE (string->number (vector-ref (current-command-line-arguments) 0)))
;(define REPS (string->number (vector-ref (current-command-line-arguments) 1)))

(define out null)

(define vec1 (for/vector ([i (in-range SIZE)])
               (random 100)))


(require (for-syntax racket/syntax))
(require (for-syntax racket/base))

(define-for-syntax ops '(+ - * /))

(define-syntax (test stx)
  (syntax-case stx ()
    [( _ type )
     #`(for ([i  vec1])
               (let* (
                      #,@(for/list ([x (in-range 10)]))
                      [x i]
                      [y (+ 3 x)]
                      [z (* y x)]
                      [a (+ z y)]
                      )
                 (set! out a)))]))



(test "foo")
(write out)

