#lang pycket #:stdlib

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))

(define (compose h i) (lambda (x) (h (i x))))


(define enumFromTo
  (lambda (m n)
    (if (> m n) '() (cons m (enumFromTo (+ m 1) n)))))

(define f
  (lambda (m)
    (* m m)))

(define g
  (lambda (m)
    (+ (* 3 m) (* m m 0.2))))

(time  (map (compose f g) (enumFromTo 0 SIZE)))
