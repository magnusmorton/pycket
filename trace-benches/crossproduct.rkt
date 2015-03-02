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
 (map  (lambda (lnum)(time (foldl (lambda (acc rnum) (+ acc ( * lnum rnum ))) 0 r))) l))

;; (define (cross-product l r)
;;     (for/list ([i l]
;;                [j r])
;;         (* i j)))
        

;; dot-product works on sequences such as vectors:
(cross-product vec1 vec2)
