#lang pycket #:stdlib

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))
(define vec (make-vector SIZE))

(define enumFromTo
  (lambda (m n)
    (begin0
        (if (> m n) '() (cons m (enumFromTo (+ m 1) n)))
      (vec-set! vec m n)
      )
    )

  )

(define sum
  (lambda (_list)
    (foldl (lambda (s x) (+ s x)) 0 _list)))



(time  (enumFromTo 1 SIZE))
