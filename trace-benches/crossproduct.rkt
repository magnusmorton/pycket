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


(define (cross-product l r)
  (if (= 0 (length l)) null
      (cons (foldl (lambda (acc  num) (+ acc (* (car l) num))) 0 r) (cross-product (cdr l) r))
      )
)






;; dot-product works on sequences such as vectors:
(time  (cross-product vec1 vec2))
