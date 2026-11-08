;;; BlackJack advisor - CLIPS rule base
;;; Authors: Hosofschi Mircea Nicolae, Mihaila Cosmin (Expert Systems course project)
;;;
;;; Card values: 2-10, 10 for J/Q/K, 11 for the Ace.
;;; Facts asserted by the host program (see blackjack_expert/engine.py):
;;;   (player (id 1) (card1 c1) (card2 c2) (total t) (soft yes|no))
;;;   (dealer (card up-card))
;;;   (goal (type choose-action) (player-id 1))
;;; The rules assert (action (player-id 1) (move hit|stand|double|split)).
;;; Several rules may fire for one hand; the host picks by priority
;;; split > double > stand > hit.
;;;
;;; The rules below are the original version, unchanged apart from this header.
;;; Hands they do not cover are listed in the README (and handled by
;;; rules/blackjack_fallback.clp, which is optional).

;; templates (facts the rules work with)

(deftemplate player
   (slot id)
   (slot total)
   (slot card1)
   (slot card2)
   (slot soft (default no))
)

(deftemplate dealer
   (slot card)
)

(deftemplate goal
   (slot type)
   (slot player-id)
)

(deftemplate action
   (slot player-id)
   (slot move)
)

(defrule alegere-actiune
   (player (id ?p) (total ?t))
   (dealer (card ?d))
   =>
   (assert (goal (type choose-action) (player-id ?p)))
)

(defrule verificare-split
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (card1 ?x) (card2 ?x))
   =>
   (assert (goal (type check-split) (player-id ?p)))
)

(defrule split-pereche
   (declare (salience 100))
   (goal (type check-split) (player-id ?p))
   (player (id ?p) (card1 ?x&:(or (= ?x 8) (= ?x 11))))
   =>
   (assert (action (player-id ?p) (move split)))
)

(defrule verificare-double
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (total ?t&:(or (= ?t 9) (= ?t 10) (= ?t 11))))
   =>
   (assert (goal (type check-double) (player-id ?p)))
)

(defrule double
   (declare (salience 90))
   (goal (type check-double) (player-id ?p))
   (player (id ?p) (total 11))
   (dealer (card ?d&:(and (>= ?d 2) (<= ?d 10))))
   =>
   (assert (action (player-id ?p) (move double)))
)

(defrule verificare-soft
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (soft yes))
   =>
   (assert (goal (type check-soft) (player-id ?p)))
)

(defrule soft-stand
   (declare (salience 80))
   (goal (type check-soft) (player-id ?p))
   (player (id ?p) (total 18))
   =>
   (assert (action (player-id ?p) (move stand)))
)

(defrule stand-total-mare
   (declare (salience 50))
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (total ?t&:(>= ?t 17)))
   =>
   (assert (action (player-id ?p) (move stand)))
)

(defrule hit-total-mic
   (declare (salience 10))
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (total ?t&:(<= ?t 11)) (card1 ?c1) (card2 ?c2))
   (test (neq ?c1 ?c2))
   =>
   (assert (action (player-id ?p) (move hit)))
)

(defrule stand-dealer-slab
   (declare (salience 40))
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (total ?t&:(and (>= ?t 12) (<= ?t 16))))
   (dealer (card ?d&:(and (>= ?d 2) (<= ?d 6))))
   =>
   (assert (action (player-id ?p) (move stand)))
)

(defrule hit-dealer-puternic
   (declare (salience 20))
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (total ?t&:(and (>= ?t 12) (<= ?t 16))) (card1 ?c1) (card2 ?c2))
   (dealer (card ?d&:(>= ?d 7)))
   (test (neq ?c1 ?c2))
   =>
   (assert (action (player-id ?p) (move hit)))
)
