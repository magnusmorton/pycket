#lang racket/base

(require racket/stream)

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0)))
(define REPS (string->number (vector-ref (current-command-line-arguments) 1)))



;; inputs; SIZE should be <= 2 * 10^6 to make sure we don't exceed word size
(define vec1 (make-vector (+ 3 SIZE) 3))
(define vec2 (in-range 5 (+ 5 SIZE)))

(define s "abcdef")

(define b #f)

(define (dot u v) (for/sum ([x u] [y v]) (* x y)))
(require (for-syntax racket/syntax))
(require (for-syntax racket/base))
(define-syntax (looper stx)
  (syntax-case stx ()
    [( _ type  )
     #`(time (for ([i (in-range REPS)])
               (begin
                 #,@(for/list ([x (in-range  100)])
                      (case (modulo x 10)
                        [(0 1 2 9)#`(vector-set! vec1 i (* 123.34 #,(random 10)) )]
                        [(3 4 5) #'(set! s (string-append  s "789"))]
                        [(6 7 8) #`(set! b (< 50 #,(random 100)))]
                        [else #'(set! s "abcdef")]
                        )))))
     ]
  ))


(define-syntax (nested stx)
  (syntax-case stx ()
    [( _ type  )
     #`(for ([j (in-range 2000)])
         (time (for ([i (in-range REPS)])
                 (begin
                   #,@(for/list ([x (in-range  10)])
                        #`(vector-set! vec1 i (* 123.34 #,(random 10)) ))))))
     ]
  ))


(looper "foo" )
