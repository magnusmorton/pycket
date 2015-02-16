#lang pycket
(require racket/list)

(define SIZE (string->number (vector-ref (current-command-line-arguments) 0 )))

(define vec (make-vector SIZE))

(define (merge-lists left right)
  (cond
    [(null? left) right]                                   ;if left is empty, return right
    [(null? right) left]                                   ;if right is empty, return left
    [(< (car left) (car right))                            ;if the head of list "left" is bigger than head of list "right"
     (cons (car left) (merge-lists (cdr left) right))]     ;cons head left to (recurse)
    [#t                                                    ;I use true as an else cond here - possibly bad style?
     (cons (car right) (merge-lists left (cdr right)))]))  ;cons head right to (recurse)

(define (merge-sort left)
  (cond
    [(or (null? left) (null? (cdr left))) left]
    [(null? (cddr left))
     (merge-lists (list (car left)) (cdr left))]
    [#t
     (let ([x (ceiling (/ (length left) 2))])
       (merge-lists (merge-sort (take left x))
                    (merge-sort (drop left x))))]))

(let loop ([i 0])
  (if (< i SIZE)
      (begin
        (vector-set! vec i (- SIZE i))
        (loop (+ 1 i)))
      #f))

(define unsorted (build-list SIZE (lambda (x) (- SIZE x))))

(time (merge-sort unsorted))
