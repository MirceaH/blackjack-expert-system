"""Thin wrapper around the CLIPS rule base (via clipspy)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import clips

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"
BASE_RULES = RULES_DIR / "blackjack.clp"
FALLBACK_RULES = RULES_DIR / "blackjack_fallback.clp"

# When several rules fire, the most "specific" move wins.
PRIORITY = ("split", "double", "stand", "hit")


def calc_total(cards: Sequence[int]) -> tuple[int, bool]:
    """Best hand value and whether it is soft (an Ace still counts as 11)."""
    total = sum(cards)
    aces = sum(1 for c in cards if c == 11)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total, aces > 0 and total <= 21


@dataclass(frozen=True)
class Advice:
    move: str
    candidates: tuple[str, ...]  # every move some rule recommended
    covered: bool  # False if no rule fired and the default was used


class Advisor:
    """Asks the CLIPS expert system what to do with a hand.

    extended=True also loads rules/blackjack_fallback.clp, which fills the
    gaps of the original rule base.
    """

    def __init__(self, extended: bool = False, default: str = "stand") -> None:
        self.default = default
        self._cache: dict[tuple, Advice] = {}  # the rule base is deterministic, so memoise
        self._env = clips.Environment()
        self._env.load(str(BASE_RULES))
        if extended:
            self._env.load(str(FALLBACK_RULES))

    def advise(self, hand: Sequence[int], dealer_card: int, allow_split: bool = True) -> Advice:
        if len(hand) < 2:
            return Advice(self.default, (), False)
        total, soft = calc_total(hand)
        key = (hand[0], hand[1], total, soft, dealer_card, allow_split)
        if key in self._cache:
            return self._cache[key]
        env = self._env
        env.reset()
        env.assert_string(
            f"(player (id 1) (card1 {hand[0]}) (card2 {hand[1]}) "
            f"(total {total}) (soft {'yes' if soft else 'no'}))"
        )
        env.assert_string(f"(dealer (card {dealer_card}))")
        env.assert_string("(goal (type choose-action) (player-id 1))")
        env.run()
        found = {str(f["move"]) for f in env.facts() if f.template.name == "action"}
        if not allow_split:
            found.discard("split")
        advice = Advice(self.default, (), False)
        for move in PRIORITY:
            if move in found:
                advice = Advice(move, tuple(m for m in PRIORITY if m in found), True)
                break
        self._cache[key] = advice
        return advice
