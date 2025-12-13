"""
Fixed Poker Hand Evaluator - Corrects all bugs
"""

from typing import List, Tuple
from abstracts import AbstractHandEvaluator


class PokerHandEvaluator(AbstractHandEvaluator):
    """
    Texas Hold'em hand evaluator - FIXED VERSION
    
    Key fixes:
    - Proper straight flush detection (checks same suit)
    - Correct full house with multiple trips
    - Safe tiebreaker handling
    """
    
    HAND_RANKINGS = {
        "ROYAL_FLUSH": 10,
        "STRAIGHT_FLUSH": 9,
        "FOUR_OF_A_KIND": 8,
        "FULL_HOUSE": 7,
        "FLUSH": 6,
        "STRAIGHT": 5,
        "THREE_OF_A_KIND": 4,
        "TWO_PAIR": 3,
        "ONE_PAIR": 2,
        "HIGH_CARD": 1
    }
    
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
        '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    def _parse_card(self, card: str) -> Tuple[str, str]:
        """Parse a card string into (rank, suit)."""
        if card.startswith('10'):
            return '10', card[2:]
        else:
            return card[0], card[1:]
    
    def _get_rank_value(self, rank: str) -> int:
        """Get numerical value of a card rank."""
        return self.RANK_VALUES[rank]
    
    def _sort_cards_by_rank(self, cards: List[str]) -> List[Tuple[str, str]]:
        """Sort cards by rank in descending order."""
        parsed_cards = [self._parse_card(card) for card in cards]
        return sorted(parsed_cards, key=lambda x: self._get_rank_value(x[0]), reverse=True)
    
    def _count_ranks(self, cards: List[Tuple[str, str]]) -> List[Tuple[int, int]]:
        """Count occurrences of each rank and return sorted by count then rank."""
        rank_count = {}
        for rank, suit in cards:
            rank_value = self._get_rank_value(rank)
            rank_count[rank_value] = rank_count.get(rank_value, 0) + 1
        
        return sorted([(count, rank) for rank, count in rank_count.items()], 
                     key=lambda x: (x[0], x[1]), reverse=True)
    
    def _is_flush(self, cards: List[Tuple[str, str]]) -> Tuple[bool, List[int], str]:
        """
        Check if cards form a flush and return kickers.
        
        Returns:
            (is_flush, kickers, flush_suit)
        """
        suit_count = {}
        for rank, suit in cards:
            suit_count[suit] = suit_count.get(suit, 0) + 1
        
        flush_suit = None
        for suit, count in suit_count.items():
            if count >= 5:
                flush_suit = suit
                break
        
        if not flush_suit:
            return False, [], ''
        
        flush_cards = [card for card in cards if card[1] == flush_suit]
        flush_cards_sorted = sorted(flush_cards, key=lambda x: self._get_rank_value(x[0]), reverse=True)
        kickers = [self._get_rank_value(rank) for rank, suit in flush_cards_sorted[:5]]
        
        return True, kickers, flush_suit
    
    def _is_straight(self, cards: List[Tuple[str, str]]) -> Tuple[bool, int]:
        """Check if cards form a straight and return highest card value."""
        unique_ranks = sorted(set(self._get_rank_value(rank) for rank, suit in cards), reverse=True)
        
        # Handle Ace-low straight (A,2,3,4,5)
        if 14 in unique_ranks:
            unique_ranks.append(1)
        
        consecutive_count = 1
        for i in range(len(unique_ranks) - 1):
            if unique_ranks[i] - 1 == unique_ranks[i + 1]:
                consecutive_count += 1
                if consecutive_count >= 5:
                    return True, unique_ranks[i - 3]
            else:
                consecutive_count = 1
        
        return False, 0
    
    def _is_straight_flush(self, cards: List[Tuple[str, str]], flush_suit: str) -> Tuple[bool, int]:
        """
        ✅ FIX: Check if flush cards ALSO form a straight
        
        Args:
            cards: All cards
            flush_suit: The suit that has 5+ cards
        
        Returns:
            (is_straight_flush, highest_card)
        """
        # Get only cards in the flush suit
        flush_cards = [card for card in cards if card[1] == flush_suit]
        
        if len(flush_cards) < 5:
            return False, 0
        
        # Check for straight within flush cards only
        unique_ranks = sorted(set(self._get_rank_value(rank) for rank, suit in flush_cards), reverse=True)
        
        # Handle Ace-low straight
        if 14 in unique_ranks:
            unique_ranks.append(1)
        
        consecutive_count = 1
        for i in range(len(unique_ranks) - 1):
            if unique_ranks[i] - 1 == unique_ranks[i + 1]:
                consecutive_count += 1
                if consecutive_count >= 5:
                    return True, unique_ranks[i - 3]
            else:
                consecutive_count = 1
        
        return False, 0
    
    def evaluate_hand(self, cards: List[str]) -> Tuple[int, List[int]]:
        """
        Evaluate a poker hand - FIXED VERSION
        
        Returns:
            (hand_rank, tiebreakers)
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate hand")
        
        parsed_cards = self._sort_cards_by_rank(cards)
        
        # Check for flush
        is_flush, flush_kickers, flush_suit = self._is_flush(parsed_cards)
        
        # ✅ FIX: Check for straight flush properly
        if is_flush:
            is_straight_flush, sf_high = self._is_straight_flush(parsed_cards, flush_suit)
            
            # Royal Flush
            if is_straight_flush and sf_high == 14:
                return self.HAND_RANKINGS["ROYAL_FLUSH"], []
            
            # Straight Flush
            if is_straight_flush:
                return self.HAND_RANKINGS["STRAIGHT_FLUSH"], [sf_high]
        
        # Check for regular straight
        is_straight, straight_high = self._is_straight(parsed_cards)
        
        # Count ranks
        rank_counts = self._count_ranks(parsed_cards)
        
        # Four of a Kind
        if rank_counts[0][0] == 4:
            four_rank = rank_counts[0][1]
            kicker = rank_counts[1][1] if len(rank_counts) > 1 else 2  # ✅ FIX: default to 2 not 0
            return self.HAND_RANKINGS["FOUR_OF_A_KIND"], [four_rank, kicker]
        
        # Full House
        # ✅ FIX: Handle multiple three-of-a-kinds correctly
        if rank_counts[0][0] == 3:
            three_rank = rank_counts[0][1]
            
            # Check if there's a pair OR another three-of-a-kind
            if len(rank_counts) > 1 and rank_counts[1][0] >= 2:
                two_rank = rank_counts[1][1]
                return self.HAND_RANKINGS["FULL_HOUSE"], [three_rank, two_rank]
        
        # Flush
        if is_flush:
            return self.HAND_RANKINGS["FLUSH"], flush_kickers[:5]
        
        # Straight
        if is_straight:
            return self.HAND_RANKINGS["STRAIGHT"], [straight_high]
        
        # Three of a Kind
        if rank_counts[0][0] == 3:
            three_rank = rank_counts[0][1]
            # ✅ FIX: Safely get kickers
            kickers = []
            for i in range(1, min(3, len(rank_counts))):
                kickers.append(rank_counts[i][1])
            # Pad with 2s if needed
            while len(kickers) < 2:
                kickers.append(2)
            return self.HAND_RANKINGS["THREE_OF_A_KIND"], [three_rank] + kickers[:2]
        
        # Two Pair
        if rank_counts[0][0] == 2 and len(rank_counts) > 1 and rank_counts[1][0] == 2:
            high_pair = rank_counts[0][1]
            low_pair = rank_counts[1][1]
            # ✅ FIX: Safe kicker
            kicker = rank_counts[2][1] if len(rank_counts) > 2 else 2
            return self.HAND_RANKINGS["TWO_PAIR"], [high_pair, low_pair, kicker]
        
        # One Pair
        if rank_counts[0][0] == 2:
            pair_rank = rank_counts[0][1]
            # ✅ FIX: Safely get 3 kickers
            kickers = []
            for i in range(1, min(4, len(rank_counts))):
                kickers.append(rank_counts[i][1])
            # Pad with 2s if needed
            while len(kickers) < 3:
                kickers.append(2)
            return self.HAND_RANKINGS["ONE_PAIR"], [pair_rank] + kickers[:3]
        
        # High Card
        # ✅ FIX: Ensure 5 kickers
        high_cards = [rc[1] for rc in rank_counts[:5]]
        while len(high_cards) < 5:
            high_cards.append(2)
        return self.HAND_RANKINGS["HIGH_CARD"], high_cards[:5]
    
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
            
            return 0