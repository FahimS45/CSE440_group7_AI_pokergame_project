from abc import ABC, abstractmethod
from typing import List, Tuple

#------1. Card Class------

class AbstractCardSystem(ABC):

    @abstractmethod
    def __init__(self) -> None:
        """Define cards and create decks in the __init__ constructor method"""
        pass

    @abstractmethod
    def shuffle(self):
        """Shuffle the deck of cards"""
        pass

    @abstractmethod
    def deal(self, num_cards: int) -> List[Tuple[str, str]]:
        """Deal a specified number of cards from the deck"""
        pass


#------2. Hand Evaluator------

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
    

#------3. Player------
class AbstractPlayer(ABC):

    @abstractmethod
    def __init__(self, name: str, chips: int) -> None:
        """
        Initialize player with a name, chip stack,
        cards (default []), current_bet (default 0) and
        folded (default False).
        """
        pass
    
    @abstractmethod
    def make_decision(self, game_state) -> str:
        """
        Choose an action (e.g., 'fold', 'check', 'call', 'raise').
        game_state: the current GameState object.
        """
        pass

    @abstractmethod
    def update_stack(self, amount: int):
        """Update player's chip count."""
        pass

    @abstractmethod
    def reset_hand(self):
        """Reset player's cards and bets between rounds."""
        pass


#------4. Agent (AI)------

class AbstractAgent(ABC):
    """Defines the interface for AI decision-making."""
    
    @abstractmethod
    def act(self, game_state):
        """Return an action based on the current state."""
        pass

    @abstractmethod
    def evaluate_state(self, game_state) -> float:
        """Return a numeric value estimating how good the current state is."""
        pass

    @abstractmethod
    def observe(self, game_state, action: str, reward: float):
        """Record feedback for learning-based agents."""
        pass


#------5. Game State------

class AbstractGameState(ABC):
    @abstractmethod
    def __init__(self, players: List[AbstractPlayer]) -> None:
        """Initialize game state with players, community cards, pot, etc."""
        pass

    @abstractmethod
    def next_player(self):
        """Advance to the next player's turn."""
        pass

    @abstractmethod
    def reset_round(self):
        """Reset values between rounds (e.g., after a showdown)."""
        pass