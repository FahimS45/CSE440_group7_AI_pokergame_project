import unittest
from hand_evaluator import PokerHandEvaluator

class TestPokerHandEvaluator(unittest.TestCase):
    
    def setUp(self):
        self.evaluator = PokerHandEvaluator()
    
    def test_royal_flush(self):
        hand = ['10S', 'JS', 'QS', 'KS', 'AS']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 9)  # Straight flush
        self.assertEqual(tiebreakers, [14])
    
    def test_straight_flush(self):
        hand = ['9H', '10H', 'JH', 'QH', 'KH']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 9)
        self.assertEqual(tiebreakers, [13])
    
    def test_four_of_a_kind(self):
        hand = ['5S', '5H', '5D', '5C', 'AS']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 8)
        self.assertEqual(tiebreakers, [5, 14])
    
    def test_full_house(self):
        hand = ['8S', '8H', '8D', 'KC', 'KH']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 7)
        self.assertEqual(tiebreakers, [8, 13])
    
    def test_flush(self):
        hand = ['2D', '5D', '7D', '9D', 'QD']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 6)
        self.assertEqual(tiebreakers, [12, 9, 7, 5, 2])
    
    def test_straight(self):
        hand = ['6C', '7H', '8S', '9D', '10C']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 5)
        self.assertEqual(tiebreakers, [10])
    
    def test_wheel_straight(self):
        hand = ['AS', '2H', '3D', '4C', '5S']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 5)
        self.assertEqual(tiebreakers, [5])
    
    def test_three_of_a_kind(self):
        hand = ['JS', 'JH', 'JD', '4C', '7S']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 4)
        self.assertEqual(tiebreakers, [11, 7, 4])
    
    def test_two_pair(self):
        hand = ['9S', '9H', '4D', '4C', 'AS']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 3)
        self.assertEqual(tiebreakers, [9, 4, 14])
    
    def test_one_pair(self):
        hand = ['QS', 'QH', '8D', '3C', '2S']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 2)
        self.assertEqual(tiebreakers, [12, 8, 3, 2])
    
    def test_high_card(self):
        hand = ['AS', 'KD', 'QC', 'JH', '9S']
        rank, tiebreakers = self.evaluator.evaluate_hand(hand)
        self.assertEqual(rank, 1)
        self.assertEqual(tiebreakers, [14, 13, 12, 11, 9])
    
    def test_hand_comparison(self):
        # Test hand1 wins (flush vs straight)
        hand1 = ['2D', '5D', '7D', '9D', 'QD']  # Flush
        hand2 = ['6C', '7H', '8S', '9D', '10C']  # Straight
        result = self.evaluator.compare_hands(hand1, hand2)
        self.assertEqual(result, 1)
        
        # Test hand2 wins (full house vs two pair)
        hand1 = ['9S', '9H', '4D', '4C', 'AS']  # Two pair
        hand2 = ['8S', '8H', '8D', 'KC', 'KH']  # Full house
        result = self.evaluator.compare_hands(hand1, hand2)
        self.assertEqual(result, -1)
        
        # Test tie (same high cards)
        hand1 = ['AS', 'KD', 'QC', 'JH', '9S']
        hand2 = ['AH', 'KS', 'QD', 'JC', '9H']
        result = self.evaluator.compare_hands(hand1, hand2)
        self.assertEqual(result, 0)
    
    def test_same_rank_different_kickers(self):
        # Both have pair of 10s, but different kickers
        hand1 = ['10S', '10H', 'AS', 'KD', '3C']  # A, K kickers
        hand2 = ['10D', '10C', 'AS', 'QD', '4C']  # A, Q kickers
        result = self.evaluator.compare_hands(hand1, hand2)
        self.assertEqual(result, 1)  # hand1 wins with better kicker

if __name__ == '__main__':
    unittest.main()