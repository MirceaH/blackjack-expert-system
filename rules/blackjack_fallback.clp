;;; Optional gap-filling rules (added later, not part of the original project).
;;; Load AFTER rules/blackjack.clp. They only fire when no other rule has
;;; produced an action for the player, so they never override the originals.
;;; Found with the exhaustive check in tests/test_coverage.py: the original
;;; rules give no advice for pairs of 2s-5s, and for 6-6 / 7-7 against a
;;; dealer 7 or higher (the host program then defaults to STAND).

(defrule fallback-hit-low-total
   (declare (salience 5))
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (total ?t&:(<= ?t 11)))
   (not (action (player-id ?p)))
   =>
   (assert (action (player-id ?p) (move hit)))
)

(defrule fallback-hit-vs-strong-dealer
   (declare (salience 5))
   (goal (type choose-action) (player-id ?p))
   (player (id ?p) (total ?t&:(and (>= ?t 12) (<= ?t 16))))
   (dealer (card ?d&:(>= ?d 7)))
   (not (action (player-id ?p)))
   =>
   (assert (action (player-id ?p) (move hit)))
)
