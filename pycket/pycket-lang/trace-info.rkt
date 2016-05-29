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
  (void))

;; returns hash of tuples (representing all fragments)
;; key is loop/label/guard id
;; value is fragment cost
(define (get-trace-db)
  (void))

(define (get-guards)
  (void))

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
