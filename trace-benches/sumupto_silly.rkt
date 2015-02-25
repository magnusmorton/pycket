#lang pycket #:stdlib

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))
(define vec (make-vector SIZE))

(define enumFromTo
  (lambda (m n)
    (begin0
        (if (> m n) '() (cons m (enumFromTo (+ m 1) n)))
      (vector-set! vec (abs (- m 2)) n)
      )
    )

  )

(define sum
  (lambda (_list)
    (foldl (lambda (s x) (+ s x)) 0 _list)))

(let loop ([i 0])
  (if (< i SIZE)
      (begin
        (vector-set! vec i (- SIZE i))
        (loop (+ 1 i)))
      #f))

(time  (enumFromTo 1 SIZE))
