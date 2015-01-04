#lang pycket #:stdlib

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Sum of Euler's totient function

(define enumFromTo
  (lambda (m n)
    (if (> m n) '() (cons m (enumFromTo (+ m 1) n)))))

(define sum
  (lambda (_list)
    (foldl (lambda (s x) (+ s x)) 0 _list)))

(define gcd
  (lambda (a b)
    (if (= b 0) a (gcd b (modulo a b)))))

(define totient
  (lambda (n)
    (length (filter (lambda (k) (= (gcd n k) 1)) (enumFromTo 1 n)))))

(define sum_totient
  (lambda (lower upper)
    (sum (map totient (enumFromTo lower upper)))))

;; timed call
(printf "(sum_totient 1 2000)\n")
(time (printf "~a\n" (sum_totient 1 2000)))
