from abc import ABC, abstractmethod
from typing import List, Tuple
from collections import Counter

class AbstractHandEvaluator(ABC):
    """Defines how poker hands are evaluated and compared."""
    
    @abstractmethod
    def evaluate_hand(self, cards: List[str]) -> Tuple[int, List[int]]:
        """
        Given a list of cards (e.g., ['AS', 'KH', 'QC', 'JD', '10S']),
        return a tuple (rank_value, tiebreaker_list).
        """
        pass

    @abstractmethod
    def compare_hands(self, hand1: List[str], hand2: List[str]) -> int:
        """
        Compare two hands.
        Return:
          1 if hand1 wins,
          -1 if hand2 wins,
          0 if tie.
        """
        pass


class PokerHandEvaluator(AbstractHandEvaluator):
    """
    Texas Hold'em hand evaluator that follows the standard poker hand rankings.
    Hand rankings (higher number = better hand):
    9 - Straight Flush
    8 - Four of a Kind
    7 - Full House
    6 - Flush
    5 - Straight
    4 - Three of a Kind
    3 - Two Pair
    2 - One Pair
    1 - High Card
    """
    
    # Card rank to value mapping
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    def __init__(self):
        pass
    
    def _parse_card(self, card: str) -> Tuple[int, str]:
        """Convert card string to (rank_value, suit) tuple."""
        # Handle 10 as a special case (2-character rank)
        if card.startswith('10'):
            return (10, card[2:])
        else:
            rank_str = card[0]
            suit = card[1:]
            return (self.RANK_VALUES[rank_str], suit)
    
    def _get_ranks_and_suits(self, cards: List[str]) -> Tuple[List[int], List[str]]:
        """Extract ranks and suits from card list."""
        ranks = []
        suits = []
        for card in cards:
            rank_val, suit = self._parse_card(card)
            ranks.append(rank_val)
            suits.append(suit)
        return ranks, suits
    
    def _is_flush(self, suits: List[str]) -> bool:
        """Check if all cards are the same suit."""
        return len(set(suits)) == 1
    
    def _is_straight(self, ranks: List[int]) -> Tuple[bool, int]:
        """Check if ranks form a straight and return highest card."""
        sorted_ranks = sorted(set(ranks))
        
        # Check for regular straight
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i+4] - sorted_ranks[i] == 4:
                return True, sorted_ranks[i+4]
        
        # Check for wheel (A-2-3-4-5)
        if set([14, 2, 3, 4, 5]).issubset(set(ranks)):
            return True, 5  # 5 is the high card for wheel
        
        return False, 0
    
    def _get_rank_counts(self, ranks: List[int]) -> List[Tuple[int, int]]:
        """Get counts of each rank, sorted by frequency then rank."""
        counter = Counter(ranks)
        # Sort by count (descending), then by rank (descending)
        return sorted(counter.items(), key=lambda x: (x[1], x[0]), reverse=True)
    
    def evaluate_hand(self, cards: List[str]) -> Tuple[int, List[int]]:
        """
        Evaluate a poker hand and return (hand_rank, tiebreakers).
        
        Args:
            cards: List of card strings (e.g., ['AS', 'KH', 'QC', 'JD', '10S'])
            
        Returns:
            Tuple of (hand_rank, tiebreaker_list)
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate hand")
        
        ranks, suits = self._get_ranks_and_suits(cards)
        rank_counts = self._get_rank_counts(ranks)
        
        is_flush = self._is_flush(suits)
        is_straight, straight_high = self._is_straight(ranks)
        
        # Check for straight flush
        if is_flush and is_straight:
            # Check for royal flush
            if straight_high == 14 and set(ranks) == {10, 11, 12, 13, 14}:
                return 9, [14]  # Royal flush
            return 9, [straight_high]  # Straight flush
        
        # Check for four of a kind
        if rank_counts[0][1] == 4:
            four_rank = rank_counts[0][0]
            kicker = rank_counts[1][0]
            return 8, [four_rank, kicker]
        
        # Check for full house
        if rank_counts[0][1] == 3 and rank_counts[1][1] >= 2:
            three_rank = rank_counts[0][0]
            pair_rank = rank_counts[1][0]
            return 7, [three_rank, pair_rank]
        
        # Check for flush
        if is_flush:
            flush_ranks = sorted(ranks, reverse=True)[:5]
            return 6, flush_ranks
        
        # Check for straight
        if is_straight:
            return 5, [straight_high]
        
        # Check for three of a kind
        if rank_counts[0][1] == 3:
            three_rank = rank_counts[0][0]
            kickers = [r for r, _ in rank_counts[1:3]]
            return 4, [three_rank] + kickers
        
        # Check for two pair
        if rank_counts[0][1] == 2 and rank_counts[1][1] == 2:
            pairs = sorted([rank_counts[0][0], rank_counts[1][0]], reverse=True)
            kicker = rank_counts[2][0]
            return 3, pairs + [kicker]
        
        # Check for one pair
        if rank_counts[0][1] == 2:
            pair_rank = rank_counts[0][0]
            kickers = [r for r, _ in rank_counts[1:4]]
            return 2, [pair_rank] + kickers
        
        # High card
        high_cards = sorted(ranks, reverse=True)[:5]
        return 1, high_cards
    
    def compare_hands(self, hand1: List[str], hand2: List[str]) -> int:
        """
        Compare two poker hands.
        
        Returns:
            1 if hand1 wins, -1 if hand2 wins, 0 if tie
        """
        rank1, tiebreakers1 = self.evaluate_hand(hand1)
        rank2, tiebreakers2 = self.evaluate_hand(hand2)
        
        # Compare hand ranks
        if rank1 > rank2:
            return 1
        elif rank1 < rank2:
            return -1
        else:
            # Same hand rank, compare tiebreakers
            for tb1, tb2 in zip(tiebreakers1, tiebreakers2):
                if tb1 > tb2:
                    return 1
                elif tb1 < tb2:
                    return -1
            return 0  # Complete tie