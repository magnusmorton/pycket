#lang pycket

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))
;(define count 0)

(define numb1 1000)
(define numb2 SIZE)

;; (for* ([i (in-range numb1)]
;;        [j (in-range numb2)])
;;       (set! count (+ 1 count))
;; )

(define inner
  (lambda (iter acc)
    (if (> iter numb2)
	acc
	(inner (+ iter 1) (+ acc 1)))))

(define outer
  (lambda (iter acc)
    (if (> iter numb1)
	acc
	(outer (+ iter 1)  (time(inner 0 acc))))))

(outer 0 0)
