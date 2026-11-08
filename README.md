# BlackJack Expert System (CLIPS + Python)

A rule-based **expert system** that advises a blackjack player whether to **hit, stand, double or split**. The knowledge base is written in [CLIPS](https://www.clipsrules.net/); Python drives it through [clipspy](https://github.com/noxdafox/clipspy). It was built as a course project (Expert Systems / *Sisteme bazate pe cunoștințe*) at "Gheorghe Asachi" Technical University of Iași by Mircea Hosofschi and Cosmin Mihăilă.

The repository contains:

| Path | What it is |
|---|---|
| `rules/blackjack.clp` | The original CLIPS rule base (templates + 11 rules) |
| `rules/blackjack_fallback.clp` | Optional extra rules that close the gaps found by testing (see below) |
| `blackjack_expert/engine.py` | `Advisor` – asserts facts, runs the rules, returns the advice |
| `blackjack_expert/game.py` | A small blackjack engine used to simulate play |
| `notebooks/BlackJack_Expert_Colab.ipynb` | The original Google Colab notebook with the guided, clickable card-table interface |
| `tests/` | pytest suite, including an exhaustive check of every two-card hand |

## How it works

For each decision Python asserts three kinds of facts and lets the inference engine run:

```clips
(player (id 1) (card1 8) (card2 8) (total 16) (soft no))
(dealer (card 10))
(goal   (type choose-action) (player-id 1))
```

The rules chain through intermediate goals (`check-split`, `check-double`, `check-soft`) and finally assert `(action (move …))`. More than one rule can fire for a hand, so conflict resolution uses **salience** inside CLIPS and a fixed priority outside it: `split > double > stand > hit`.

| Situation | Advice |
|---|---|
| Pair of 8s or Aces | split |
| Hard 11 against a dealer 2–10 | double |
| Soft 18 (Ace + 7) | stand |
| Total 17 or more | stand |
| Total 12–16, dealer shows 2–6 | stand |
| Total 12–16, dealer shows 7 or more | hit |
| Total 11 or less | hit |

Card values: 2–10, 10 for J/Q/K, 11 for the Ace (reduced to 1 automatically when the hand would bust).

## Run it

```bash
pip install -r requirements.txt

# ask the expert system directly
python - <<'PY'
from blackjack_expert import Advisor
advisor = Advisor(extended=True)
print(advisor.advise([8, 8], dealer_card=10))   # Advice(move='split', ...)
print(advisor.advise([10, 3], dealer_card=10))  # Advice(move='hit', ...)
PY

# tests
python -m pytest
```

To play with the clickable interface, open `notebooks/BlackJack_Expert_Colab.ipynb` in Google Colab and run all cells. It installs clipspy, writes the `.clp` file and shows a card table with the expert's recommendation.

## What testing found

Because there are only 550 distinct two-card situations (10 card values × 10 card values, unordered, × 10 dealer up-cards), the rule base can be checked exhaustively (`tests/test_advisor.py`):

- **50 hands get no advice from the original rules** – pairs of 2s, 3s, 4s and 5s against any dealer card, and 6-6 / 7-7 against a dealer 7 or higher. The reason is that the generic hit rules require the two cards to be different, to avoid fighting the split rules. The interface then fell back to *stand*, which is wrong for a hand like 2-2.
- `rules/blackjack_fallback.clp` adds two low-priority rules that only fire when nothing else did. A test checks that they cover all 550 situations and never change an answer the original rules already gave.
- Simulated over 100,000 rounds each (infinite deck, no blackjack bonus, dealer stands on 17, one card on double, split without re-splitting; seed 1):

| Rule set | Win | Loss | Push | Average result per round (1 unit stake) |
|---|---|---|---|---|
| Original | 42.2 % | 48.8 % | 9.1 % | −0.058 |
| With fallback rules | 42.7 % | 48.0 % | 9.3 % | −0.045 |

Blackjack always favours the house; these numbers show the advice is sound for a compact rule base but not perfect basic strategy. Soft totals other than 18, doubling on 9/10 and several pair decisions are not modelled.

## Possible next steps

- Add the missing basic-strategy rules (soft doubles, doubling on 9–10, pair splitting for 2s, 3s, 6s, 7s and 9s)
- Explain each recommendation by listing the rules that fired
- Count cards instead of drawing from an infinite deck

## Authors

Hosofschi Mircea Nicolae and Mihăilă Cosmin.
