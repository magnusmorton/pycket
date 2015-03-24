#lang racket/base

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0)))
(define REPS (string->number (vector-ref (current-command-line-arguments) 1)))

;; inputs; SIZE should be <= 2 * 10^6 to make sure we don't exceed word size
(define vec1 (in-range 3 (+ 3 SIZE)))
(define vec2 (in-range 5 (+ 5 SIZE)))

;; code from Sam's ICFP'15 submission
(define (dot u v) (for/sum ([x u] [y v]) (* x y)))

;; check result stays at word size (commented out for now)
;(define result (dot vec1 vec2))
;result
;(fixnum? result)

;; loop of timed executions (time unit for pycket: microseconds)
(for ([i (in-range REPS)])
  (time (dot vec1 vec2)))
