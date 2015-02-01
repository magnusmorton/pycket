#lang pycket #:stdlib



(define enumFromTo
  (lambda (m n)
    (if (> m n) '() (cons m (enumFromTo (+ m 1) n)))))

(define sum
  (lambda (_list)
    (foldl (lambda (s x) (+ s x)) 0 _list)))

(time (printf "~a\n" (sum  (enumFromTo 1 (string->number (vector-ref (current-command-line-arguments) 0 ))))))
