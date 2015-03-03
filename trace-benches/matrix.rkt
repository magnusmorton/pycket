#lang pycket
;; The Bubble sort benchmark from Strickland et al 2012
(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))



(define (make-array-2d size initial)
  (make-vector (* size size) initial))

(define (array-2d-ref array size row col)
  (vector-ref array (+ (* row size) col)))

(define (array-2d-set! array size row col value)
  (vector-set! array (+ (* row size) col)))


(define vec (make-array-2d SIZE 3))


(define (scal-mul val matrix)
  (let loop ([i 0]
             [matrix matrix])
    (if (< i (vector-length matrix))
        (begin
          (vector-set! matrix i (* val (vector-ref matrix i)))
          (loop (+ i 1) matrix))
        0)))

(time (scal-mul 137 vec))
;(bubble-sort vec)
