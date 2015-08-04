#lang racket

(define test1 '((1 2 3 4) (1 2 3 4) (1 2 3 4) (1 2 3 4)))
(define test2 '((5 6 7 8) (5 6 7 8) (5 6 7 8) (5 6 7 8)))
(define (m-mult m1 m2)
  (for/list ([r m1])
    (m-mult-inner r m2)))

(define (m-mult-inner r m2)
  (for/list ([c (apply map list m2)])
    (apply + (map * r c))))

(define (m-mult-chunked m1 m2 n)
  (let* ([len (length m1)]
         [x (m-mult (slice m1 0 (/ len n)))]
         [y (m-mult (slice m1 2 (/ len n)))])
    (append x y)))
;;(m-mult '((1 2) (3 4)) '((5 6) (7 8)))

(m-mult test1 test2)
;; -> '((19 22) (43 50))

(define (slice l offset n)
  (take (drop l offset) n))
