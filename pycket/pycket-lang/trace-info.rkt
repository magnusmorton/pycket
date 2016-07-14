#lang racket/base
(require racket/list)
(provide
 counters
 get-trace-db
 get-guards)

;; returns hash of tuples
;; key is loop/label/guard id
;; tuple contains counter value and type (type may be removed at some point)
(define (counters)
  #hash((0 . 1000)
        (1 . 100)
        (32134 . 6700)))

(define (asm-lengths)
  #hash((0 . 5345)
        (1 . 234184)
        (283478294 . 2834)))

;; returns hash of tuples (representing all fragments)
;; key is loop/label/guard id
;; value is fragment cost
(define (get-trace-db)
  #hash((0 . ("label" "int_add" "int_sub" "int_ge" "guard_overflow" "jump"))
        (1 . ("label" "new" "new_with_vtable" "float_add" "int_ge" "guard_false"))
        (32134 . ("label" "new" "new" "newstr" "guard_exception" "getfield_gc" "getfield_gc" "setfield_gc" "guard_overflow" "jump"))))

(define (get-guards)
  #hash((0 . ((1 . 4)))
        (1 . ())
        (32134 . ((123545 . 4) (12156 . 8)))))

;; register another JIT hook
;; callback should take one argument
;; #:hook can be 'after-compile 'before-compile 'on-abort
(define (register-jit-hook callback #:hook [hook 'after-compile])
  (void))


;; returns a number
;; counters and trace-costs should be the same structure as returned in counters
;; and get-trace-db
(define (calculate-total-cost counters trace-costs )
  (void))

;; sets the cost model to use
;; model is a 5-tuple of weights or 0 for CM0
(define (set-cost-model model)
  (void))
