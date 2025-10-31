"""
Hand Evaluation System for Poker Game Simulator
CSE440 Project: Develop a Poker Game Simulator with Expectiminimax
"""

from enum import Enum
from typing import List, Tuple, Dict

class HandRank(Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class HandEvaluator:
    def __init__(self):
        self.rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, 
                           '7': 7, '8': 8, '9': 9, '10': 10, 
                           'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    def evaluate_hand(self, cards: List[Tuple[str, str]]) -> Tuple[HandRank, List[int]]:
        """
        Evaluate a poker hand and return its rank and tie-breaker values
        
        Args:
            cards: List of (rank, suit) tuples
            
        Returns:
            Tuple of (HandRank, tie_breaker_values)
        """
        if len(cards) != 5:
            raise ValueError("Hand must contain exactly 5 cards")
        
        # Check for different hand types in descending order of rank
        if self._is_royal_flush(cards):
            return (HandRank.ROYAL_FLUSH, [])
        elif self._is_straight_flush(cards):
            high_card = self._get_straight_high_card(cards)
            return (HandRank.STRAIGHT_FLUSH, [high_card])
        elif self._is_four_of_a_kind(cards):
            quad_rank, kicker = self._get_four_of_a_kind_info(cards)
            return (HandRank.FOUR_OF_A_KIND, [quad_rank, kicker])
        elif self._is_full_house(cards):
            triple_rank, pair_rank = self._get_full_house_info(cards)
            return (HandRank.FULL_HOUSE, [triple_rank, pair_rank])
        elif self._is_flush(cards):
            high_cards = self._get_flush_high_cards(cards)
            return (HandRank.FLUSH, high_cards)
        elif self._is_straight(cards):
            high_card = self._get_straight_high_card(cards)
            return (HandRank.STRAIGHT, [high_card])
        elif self._is_three_of_a_kind(cards):
            triple_rank, kickers = self._get_three_of_a_kind_info(cards)
            return (HandRank.THREE_OF_A_KIND, [triple_rank] + kickers)
        elif self._is_two_pair(cards):
            pairs, kicker = self._get_two_pair_info(cards)
            return (HandRank.TWO_PAIR, pairs + [kicker])
        elif self._is_one_pair(cards):
            pair_rank, kickers = self._get_one_pair_info(cards)
            return (HandRank.ONE_PAIR, [pair_rank] + kickers)
        else:
            high_cards = self._get_high_cards(cards)
            return (HandRank.HIGH_CARD, high_cards)
    
    def compare_hands(self, hand1: List[Tuple[str, str]], hand2: List[Tuple[str, str]]) -> int:
        """
        Compare two poker hands and return the winner
        
        Args:
            hand1: First hand as list of (rank, suit) tuples
            hand2: Second hand as list of (rank, suit) tuples
            
        Returns:
            1 if hand1 wins, -1 if hand2 wins, 0 if tie
        """
        rank1, tie_breakers1 = self.evaluate_hand(hand1)
        rank2, tie_breakers2 = self.evaluate_hand(hand2)
        
        # Compare hand ranks
        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        else:
            # Same hand rank, compare tie-breakers
            for i in range(len(tie_breakers1)):
                if tie_breakers1[i] > tie_breakers2[i]:
                    return 1
                elif tie_breakers1[i] < tie_breakers2[i]:
                    return -1
            return 0  # Complete tie
    
    def _is_royal_flush(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for royal flush (A, K, Q, J, 10 of same suit)"""
        if not self._is_flush(cards):
            return False
        
        ranks = {self.rank_values[card[0]] for card in cards}
        return ranks == {10, 11, 12, 13, 14}
    
    def _is_straight_flush(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for straight flush (straight of same suit)"""
        return self._is_flush(cards) and self._is_straight(cards)
    
    def _is_four_of_a_kind(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for four of a kind"""
        rank_counts = self._get_rank_counts(cards)
        return 4 in rank_counts.values()
    
    def _is_full_house(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for full house (three of a kind + pair)"""
        rank_counts = self._get_rank_counts(cards)
        return 3 in rank_counts.values() and 2 in rank_counts.values()
    
    def _is_flush(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for flush (all same suit)"""
        suits = {card[1] for card in cards}
        return len(suits) == 1
    
    def _is_straight(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for straight (5 consecutive ranks)"""
        rank_values = sorted([self.rank_values[card[0]] for card in cards])
        
        # Check for normal straight
        for i in range(1, 5):
            if rank_values[i] != rank_values[i-1] + 1:
                # Check for wheel straight (A-2-3-4-5)
                if set(rank_values) == {2, 3, 4, 5, 14}:
                    return True
                return False
        return True
    
    def _is_three_of_a_kind(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for three of a kind"""
        rank_counts = self._get_rank_counts(cards)
        return 3 in rank_counts.values()
    
    def _is_two_pair(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for two pair"""
        rank_counts = self._get_rank_counts(cards)
        pairs = [count for count in rank_counts.values() if count == 2]
        return len(pairs) == 2
    
    def _is_one_pair(self, cards: List[Tuple[str, str]]) -> bool:
        """Check for one pair"""
        rank_counts = self._get_rank_counts(cards)
        pairs = [count for count in rank_counts.values() if count == 2]
        return len(pairs) == 1
    
    def _get_rank_counts(self, cards: List[Tuple[str, str]]) -> Dict[int, int]:
        """Get count of each rank in the hand"""
        rank_counts = {}
        for card in cards:
            rank_val = self.rank_values[card[0]]
            rank_counts[rank_val] = rank_counts.get(rank_val, 0) + 1
        return rank_counts
    
    def _get_straight_high_card(self, cards: List[Tuple[str, str]]) -> int:
        """Get the high card of a straight (handles wheel straight)"""
        rank_values = sorted([self.rank_values[card[0]] for card in cards])
        if set(rank_values) == {2, 3, 4, 5, 14}:  # Wheel straight
            return 5
        return max(rank_values)
    
    def _get_four_of_a_kind_info(self, cards: List[Tuple[str, str]]) -> Tuple[int, int]:
        """Get four of a kind rank and kicker"""
        rank_counts = self._get_rank_counts(cards)
        quad_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
        kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
        return quad_rank, kicker
    
    def _get_full_house_info(self, cards: List[Tuple[str, str]]) -> Tuple[int, int]:
        """Get triple rank and pair rank for full house"""
        rank_counts = self._get_rank_counts(cards)
        triple_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
        pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
        return triple_rank, pair_rank
    
    def _get_flush_high_cards(self, cards: List[Tuple[str, str]]) -> List[int]:
        """Get high cards for flush (all cards in descending order)"""
        rank_values = [self.rank_values[card[0]] for card in cards]
        return sorted(rank_values, reverse=True)
    
    def _get_three_of_a_kind_info(self, cards: List[Tuple[str, str]]) -> Tuple[int, List[int]]:
        """Get triple rank and kickers for three of a kind"""
        rank_counts = self._get_rank_counts(cards)
        triple_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
        kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
        return triple_rank, kickers
    
    def _get_two_pair_info(self, cards: List[Tuple[str, str]]) -> Tuple[List[int], int]:
        """Get pair ranks and kicker for two pair"""
        rank_counts = self._get_rank_counts(cards)
        pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], reverse=True)
        kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
        return pairs, kicker
    
    def _get_one_pair_info(self, cards: List[Tuple[str, str]]) -> Tuple[int, List[int]]:
        """Get pair rank and kickers for one pair"""
        rank_counts = self._get_rank_counts(cards)
        pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
        kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
        return pair_rank, kickers
    
    def _get_high_cards(self, cards: List[Tuple[str, str]]) -> List[int]:
        """Get high cards for high card hand (all cards in descending order)"""
        rank_values = [self.rank_values[card[0]] for card in cards]
        return sorted(rank_values, reverse=True)
    
    def hand_rank_to_string(self, hand_rank: HandRank) -> str:
        """Convert HandRank enum to human-readable string"""
        return hand_rank.name.replace('_', ' ').title()