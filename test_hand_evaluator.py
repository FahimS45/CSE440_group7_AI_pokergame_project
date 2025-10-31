"""
Unit tests for Hand Evaluation System
"""

import unittest
from hand_evaluator import HandEvaluator, HandRank

class TestHandEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = HandEvaluator()
    
    def test_royal_flush(self):
        hand = [('10', 'H'), ('J', 'H'), ('Q', 'H'), ('K', 'H'), ('A', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.ROYAL_FLUSH)
    
    def test_straight_flush(self):
        hand = [('9', 'H'), ('10', 'H'), ('J', 'H'), ('Q', 'H'), ('K', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.STRAIGHT_FLUSH)
    
    def test_four_of_a_kind(self):
        hand = [('A', 'H'), ('A', 'D'), ('A', 'C'), ('A', 'S'), ('K', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.FOUR_OF_A_KIND)
    
    def test_full_house(self):
        hand = [('A', 'H'), ('A', 'D'), ('A', 'C'), ('K', 'S'), ('K', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.FULL_HOUSE)
    
    def test_flush(self):
        hand = [('2', 'H'), ('5', 'H'), ('7', 'H'), ('9', 'H'), ('K', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.FLUSH)
    
    def test_straight(self):
        hand = [('9', 'H'), ('10', 'D'), ('J', 'C'), ('Q', 'S'), ('K', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.STRAIGHT)
    
    def test_wheel_straight(self):
        hand = [('A', 'H'), ('2', 'D'), ('3', 'C'), ('4', 'S'), ('5', 'H')]
        rank, tie_breakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.STRAIGHT)
        self.assertEqual(tie_breakers[0], 5)  # High card should be 5, not Ace
    
    def test_three_of_a_kind(self):
        hand = [('A', 'H'), ('A', 'D'), ('A', 'C'), ('K', 'S'), ('Q', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.THREE_OF_A_KIND)
    
    def test_two_pair(self):
        hand = [('A', 'H'), ('A', 'D'), ('K', 'C'), ('K', 'S'), ('Q', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.TWO_PAIR)
    
    def test_one_pair(self):
        hand = [('A', 'H'), ('A', 'D'), ('K', 'C'), ('Q', 'S'), ('J', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.ONE_PAIR)
    
    def test_high_card(self):
        hand = [('A', 'H'), ('K', 'D'), ('Q', 'C'), ('J', 'S'), ('9', 'H')]
        rank, _ = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, HandRank.HIGH_CARD)
    
    def test_hand_comparison(self):
        # Royal flush vs Straight flush
        royal_flush = [('10', 'H'), ('J', 'H'), ('Q', 'H'), ('K', 'H'), ('A', 'H')]
        straight_flush = [('9', 'H'), ('10', 'H'), ('J', 'H'), ('Q', 'H'), ('K', 'H')]
        self.assertEqual(self.evaluator.compare_hands(royal_flush, straight_flush), 1)
        
        # Same hand type, different high cards
        flush1 = [('A', 'H'), ('K', 'H'), ('Q', 'H'), ('J', 'H'), ('9', 'H')]
        flush2 = [('K', 'D'), ('Q', 'D'), ('J', 'D'), ('10', 'D'), ('8', 'D')]
        self.assertEqual(self.evaluator.compare_hands(flush1, flush2), 1)
        
        # Tie
        same_hand1 = [('A', 'H'), ('K', 'D'), ('Q', 'C'), ('J', 'S'), ('10', 'H')]
        same_hand2 = [('A', 'D'), ('K', 'H'), ('Q', 'S'), ('J', 'C'), ('10', 'D')]
        self.assertEqual(self.evaluator.compare_hands(same_hand1, same_hand2), 0)
    
    def test_hand_rank_string(self):
        self.assertEqual(self.evaluator.hand_rank_to_string(HandRank.ROYAL_FLUSH), "Royal Flush")
        self.assertEqual(self.evaluator.hand_rank_to_string(HandRank.ONE_PAIR), "One Pair")

if __name__ == '__main__':
    unittest.main()