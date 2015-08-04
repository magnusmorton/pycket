#lang racket

(define test1 '((1 2 3 4) (1 2 3 4) (1 2 3 4) (1 2 3 4)))
(define test2 '((5 6 7 8) (5 6 7 8) (5 6 7 8) (5 6 7 8)))
(define (m-mult m1 m2)
  (for/list ([r m1])
    (m-mult-inner r m2)))

(define (make-mat rows cols)
  (for/list ([i cols])
    (random-list rows)))

(define (random-list size)
  (for/list ([i size])
    (random 10)))

(define (m-mult-inner r m2)
  (for/list ([c (apply map list m2)])
    (apply + (map * r c))))

(define (slice l offset n)
  (take (drop l offset) n))

(define (m-mult-chunked m1 m2 n)
  (let ([chunk (/ (length m1) n)])
    (apply append
            (for/list ([worker n])
              (m-mult (slice m1 (* worker chunk) chunk) m2)))))

(m-mult test1 test2)

(m-mult-chunked (make-mat 1000 100) (make-mat 100 1000) 2)
;; -> '((19 22) (43 50))



