#lang pycket #:stdlib

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))

(define (mk-list size v)
  (if (= 0 size)
      null
      (cons v (mk-list (- size 1) v))
      )
  )

(define vec1 (mk-list SIZE 3))
(define vec2 (mk-list SIZE 5))


(define (dot-product l r)
  (if (= 0 (length r)) 0
      ( + (* (car l) (car r)) (dot-product (cdr l) (cdr r)))
      )
)




;; dot-product works on sequences such as vectors:
(dot-product vec1 vec2)
