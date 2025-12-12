from typing import List, Tuple
from test_abstracts import AbstractHandEvaluator

class PokerHandEvaluator(AbstractHandEvaluator):
    """
    Texas Hold'em hand evaluator that implements the AbstractHandEvaluator interface.
    Evaluates poker hands and compares them according to standard poker rules.
    """
    
    # Hand rankings from highest to lowest
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
    
    # Card rank values for comparison
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
        '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    def _parse_card(self, card: str) -> Tuple[str, str]:
        """Parse a card string into (rank, suit)."""
        # Handle 10 as a special case since it has two characters
        if card.startswith('10'):
            return '10', card[2:]
        else:
            return card[0], card[1]
    
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
        
        # Sort by count (descending) then by rank (descending)
        return sorted([(count, rank) for rank, count in rank_count.items()], 
                     key=lambda x: (x[0], x[1]), reverse=True)
    
    def _is_flush(self, cards: List[Tuple[str, str]]) -> Tuple[bool, List[int]]:
        """Check if cards form a flush and return kickers."""
        suit_count = {}
        for rank, suit in cards:
            suit_count[suit] = suit_count.get(suit, 0) + 1
        
        # Find suit with 5 or more cards
        flush_suit = None
        for suit, count in suit_count.items():
            if count >= 5:
                flush_suit = suit
                break
        
        if not flush_suit:
            return False, []
        
        # Get flush cards sorted by rank
        flush_cards = [card for card in cards if card[1] == flush_suit]
        flush_cards_sorted = sorted(flush_cards, key=lambda x: self._get_rank_value(x[0]), reverse=True)
        kickers = [self._get_rank_value(rank) for rank, suit in flush_cards_sorted[:5]]
        
        return True, kickers
    
    def _is_straight(self, cards: List[Tuple[str, str]]) -> Tuple[bool, int]:
        """Check if cards form a straight and return highest card value."""
        unique_ranks = sorted(set(self._get_rank_value(rank) for rank, suit in cards), reverse=True)
        
        # Handle Ace-low straight (A,2,3,4,5)
        if 14 in unique_ranks:
            unique_ranks.append(1)  # Add Ace as low
        
        # Check for straight
        consecutive_count = 1
        for i in range(len(unique_ranks) - 1):
            if unique_ranks[i] - 1 == unique_ranks[i + 1]:
                consecutive_count += 1
                if consecutive_count >= 5:
                    return True, unique_ranks[i - 3]  # Highest card of straight
            else:
                consecutive_count = 1
        
        return False, 0
    
    def evaluate_hand(self, cards: List[str]) -> Tuple[int, List[int]]:
        """
        Evaluate a poker hand and return (hand_rank, tiebreaker_list).
        
        Args:
            cards: List of card strings (e.g., ['AS', 'KH', 'QC', 'JD', '10S'])
            
        Returns:
            Tuple of (hand_rank_value, tiebreaker_list)
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate hand")
        
        parsed_cards = self._sort_cards_by_rank(cards)
        
        # Check for flush and straight combinations first
        is_flush, flush_kickers = self._is_flush(parsed_cards)
        is_straight, straight_high = self._is_straight(parsed_cards)
        
        # Royal Flush
        if is_flush and is_straight and straight_high == 14 and set(flush_kickers[:5]) == {14, 13, 12, 11, 10}:
            return self.HAND_RANKINGS["ROYAL_FLUSH"], []
        
        # Straight Flush
        if is_flush and is_straight:
            return self.HAND_RANKINGS["STRAIGHT_FLUSH"], [straight_high]
        
        # Count ranks for other hand types
        rank_counts = self._count_ranks(parsed_cards)
        
        # Four of a Kind
        if rank_counts[0][0] == 4:
            four_rank = rank_counts[0][1]
            kicker = rank_counts[1][1] if len(rank_counts) > 1 else 0
            return self.HAND_RANKINGS["FOUR_OF_A_KIND"], [four_rank, kicker]
        
        # Full House
        if rank_counts[0][0] == 3 and len(rank_counts) > 1 and rank_counts[1][0] >= 2:
            three_rank = rank_counts[0][1]
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
            kickers = [rc[1] for rc in rank_counts[1:3]]  # Next two highest cards
            return self.HAND_RANKINGS["THREE_OF_A_KIND"], [three_rank] + kickers
        
        # Two Pair
        if rank_counts[0][0] == 2 and len(rank_counts) > 1 and rank_counts[1][0] == 2:
            high_pair = rank_counts[0][1]
            low_pair = rank_counts[1][1]
            kicker = rank_counts[2][1] if len(rank_counts) > 2 else 0
            return self.HAND_RANKINGS["TWO_PAIR"], [high_pair, low_pair, kicker]
        
        # One Pair
        if rank_counts[0][0] == 2:
            pair_rank = rank_counts[0][1]
            kickers = [rc[1] for rc in rank_counts[1:4]]  # Next three highest cards
            return self.HAND_RANKINGS["ONE_PAIR"], [pair_rank] + kickers
        
        # High Card
        high_cards = [rc[1] for rc in rank_counts[:5]]
        return self.HAND_RANKINGS["HIGH_CARD"], high_cards
    
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
            
            # All tiebreakers are equal
            return 0