import itertools
import random

import pytest

from blackjack_expert import Advisor, calc_total, simulate

CARDS = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11)


@pytest.fixture(scope="module")
def original() -> Advisor:
    return Advisor()


@pytest.fixture(scope="module")
def extended() -> Advisor:
    return Advisor(extended=True)


def test_calc_total_handles_aces():
    assert calc_total([11, 10]) == (21, True)
    assert calc_total([11, 11]) == (12, True)
    assert calc_total([11, 6, 10]) == (17, False)
    assert calc_total([10, 9, 5]) == (24, False)


@pytest.mark.parametrize(
    "hand,dealer,expected",
    [
        ([8, 8], 10, "split"),       # always split eights
        ([11, 11], 6, "split"),      # ... and aces
        ([5, 6], 6, "double"),       # 11 against a weak or medium dealer
        ([10, 7], 10, "stand"),      # hard 17+
        ([11, 7], 9, "stand"),       # soft 18
        ([10, 3], 5, "stand"),       # 13 against a weak dealer
        ([10, 3], 10, "hit"),        # 13 against a strong dealer
        ([3, 4], 9, "hit"),          # low total
    ],
)
def test_known_decisions(original, hand, dealer, expected):
    assert original.advise(hand, dealer).move == expected


def test_split_is_only_offered_for_pairs(original):
    for c1, c2, d in itertools.product(CARDS, CARDS, CARDS):
        if c1 != c2:
            assert original.advise([c1, c2], d).move != "split"


def test_allow_split_false_never_returns_split(original):
    assert original.advise([8, 8], 10, allow_split=False).move != "split"


def test_original_rules_have_known_gaps(original):
    """Documented in the README: no rule covers these hands (STAND is the default)."""
    uncovered = {
        (c1, c2, d)
        for c1, c2, d in itertools.product(CARDS, CARDS, CARDS)
        if c1 <= c2 and not original.advise([c1, c2], d).covered
    }
    pairs = {(c1, c2) for c1, c2, _ in uncovered}
    assert pairs == {(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)}
    assert len(uncovered) == 50


def test_fallback_rules_cover_every_two_card_hand(extended):
    for c1, c2, d in itertools.product(CARDS, CARDS, CARDS):
        assert extended.advise([c1, c2], d).covered, (c1, c2, d)


def test_fallback_rules_never_change_original_advice(original, extended):
    for c1, c2, d in itertools.product(CARDS, CARDS, CARDS):
        before = original.advise([c1, c2], d)
        if before.covered:
            assert extended.advise([c1, c2], d).move == before.move


def test_simulation_is_reproducible_and_sane(extended):
    a = simulate(extended, rounds=2000, seed=7)
    b = simulate(extended, rounds=2000, seed=7)
    assert a == b
    assert a["win_rate"] + a["loss_rate"] + a["push_rate"] == pytest.approx(1)
    assert 0.35 < a["win_rate"] < 0.5
