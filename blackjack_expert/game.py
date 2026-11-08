"""A small blackjack engine used to test the advisor by simulation.

Simplifications (same spirit as the original notebook): infinite deck, no
blackjack bonus, no re-splitting, the dealer draws to 17 and stands on any 17,
double is allowed on the first two cards and gives exactly one more card.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from .engine import Advisor, calc_total

# 10 appears four times for 10, J, Q, K; 11 is the Ace.
DECK = (2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11)


def dealer_play(hand: list[int], rng: random.Random) -> list[int]:
    hand = list(hand)
    while calc_total(hand)[0] < 17:
        hand.append(rng.choice(DECK))
    return hand


def _play_one(hand: list[int], dealer_up: int, advisor: Advisor, rng: random.Random) -> tuple[list[int], int]:
    """Play one hand following the advisor; returns (final hand, stake multiplier)."""
    first = True
    while calc_total(hand)[0] < 21:
        move = advisor.advise(hand, dealer_up, allow_split=False).move
        if move == "double" and first:
            hand.append(rng.choice(DECK))
            return hand, 2
        if move in ("hit", "double"):  # a "double" after the first move is just a hit
            hand.append(rng.choice(DECK))
            first = False
        else:
            break
    return hand, 1


def _payout(hand: list[int], dealer_hand: list[int], stake: int) -> int:
    p, d = calc_total(hand)[0], calc_total(dealer_hand)[0]
    if p > 21:
        return -stake
    if d > 21 or p > d:
        return stake
    return -stake if p < d else 0


@dataclass
class HandResult:
    player: list[list[int]]
    dealer: list[int]
    net: int  # units won (+) or lost (-)
    first_move: str


def play_hand(advisor: Advisor, rng: random.Random) -> HandResult:
    """Deal and play one round, following the advisor on every decision."""
    hand = [rng.choice(DECK), rng.choice(DECK)]
    dealer = [rng.choice(DECK), rng.choice(DECK)]
    up = dealer[0]
    first = advisor.advise(hand, up).move
    if first == "split" and hand[0] == hand[1]:
        hands = [[hand[0], rng.choice(DECK)], [hand[1], rng.choice(DECK)]]
    else:
        hands = [hand]
    played = [_play_one(h, up, advisor, rng) for h in hands]
    live = any(calc_total(h)[0] <= 21 for h, _ in played)
    final_dealer = dealer_play(dealer, rng) if live else dealer
    net = sum(_payout(h, final_dealer, s) for h, s in played)
    return HandResult([h for h, _ in played], final_dealer, net, first)


def simulate(advisor: Advisor, rounds: int = 100_000, seed: int = 0) -> dict[str, float]:
    """Play many rounds; returns win/loss/push rates and the average result per round."""
    rng = random.Random(seed)
    wins = losses = pushes = 0
    total_net = 0
    for _ in range(rounds):
        r = play_hand(advisor, rng)
        total_net += r.net
        if r.net > 0:
            wins += 1
        elif r.net < 0:
            losses += 1
        else:
            pushes += 1
    return {
        "rounds": rounds,
        "win_rate": wins / rounds,
        "loss_rate": losses / rounds,
        "push_rate": pushes / rounds,
        "avg_net_per_round": total_net / rounds,
    }
