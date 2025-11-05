# mock_support.py
from typing import List, Tuple
import random

# ----- MockCardSystem -----
class MockCardSystem:
    """Simple fake deck for testing without real Card/Deck system."""
    def __init__(self):
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def shuffle(self):
        print("Mock deck shuffled.")

    def deal(self, num_cards: int) -> List[Tuple[str, str]]:
        cards = [(random.choice(self.suits), random.choice(self.ranks)) for _ in range(num_cards)]
        return cards

# ----- MockHandEvaluator -----
class MockHandEvaluator:
    """Fake evaluator that just returns random values for now."""
    def evaluate_hand(self, cards: List[str]):
        rank_value = random.randint(1, 10)
        return (rank_value, [random.randint(1, 14) for _ in range(5)])

    def compare_hands(self, hand1: List[str], hand2: List[str]) -> int:
        # Just randomly decide a winner for testing
        result = random.choice([1, -1, 0])
        return result
