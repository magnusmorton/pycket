#lang racket

(define (random-vector size)
  (for/vector ([i size])
    (random 10)))

(define (make-mat rows cols)
  (for/vector ([i cols])
    (random-vector rows)))

(define (matmul m1 m2)
  (for/vector ([r m1])
    (for/vector ([c (apply vector-map vector (vector->list m2))])
      (for/fold ([sum 0])
                ([i (vector-map * r c)])
        (+ sum i)))))

(define (matmul-chunked m1 m2 n)
  (let ([chunk (/ (vector-length m1) n)])
    (apply vector-append
           (for/list ([worker n])
             (matmul (vector-copy m1 (* worker chunk) (+ (* worker chunk) chunk)) m2)))))
