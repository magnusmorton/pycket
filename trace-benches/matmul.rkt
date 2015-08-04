#lang racket
(define (m-mult m1 m2)
  (for/list ([r m1])
    (m-mult-inner r m2)))

(define (m-mult-inner r m2)
  (for/list ([c (apply map list m2)])
    (apply + (map * r c))))

(define (m-mult-chunked m1 m2 n) '())
(m-mult '((1 2) (3 4)) '((5 6) (7 8)))
;; -> '((19 22) (43 50))
