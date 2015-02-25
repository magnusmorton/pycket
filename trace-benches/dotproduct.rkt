#lang pycket #:stdlib

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))
(define vec1 (build-list SIZE values))
(define vec2 (build-list SIZE values))
(define (dot-product l r) 
  (if (= 0 (length r)) 0 
      ( + (* (car l) (car r)) (dot-product (cdr l) (cdr r)))
      )
)
 
 
;; dot-product works on sequences such as vectors:
(time (dot-product vec1 vec2))
