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
    def deal(self, num_cards: int) -> List[str]:
        """
        Deal a specified number of cards from the deck.
        Returns cards as strings (e.g., ['AS', 'KH', 'QC'])
        """
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

class AbstractAgent(AbstractPlayer):
    """
    Defines the interface for AI decision-making using Expectiminimax.
    Inherits from AbstractPlayer since agents are players.
    """
    
    @abstractmethod
    def act(self, game_state):
        """
        Return an action based on the current state.
        For Expectiminimax agent, this calls the search algorithm.
        """
        pass

    @abstractmethod
    def evaluate_state(self, game_state) -> float:
        """
        Return a numeric value estimating how good the current state is.
        Used as heuristic evaluation at leaf nodes.
        Higher values = better for this agent.
        """
        pass

    @abstractmethod
    def observe(self, game_state, action: str, reward: float):
        """
        Record feedback for learning-based agents.
        Note: Not used for Expectiminimax (which doesn't learn).
        """
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

    # ===== NEW METHODS FOR EXPECTIMINIMAX SUPPORT =====
    
    @abstractmethod
    def clone(self):
        """
        Create a deep copy of the current game state.
        Essential for Expectiminimax tree search - allows simulation
        of future states without modifying the real game.
        
        Returns:
            A completely independent copy of this game state.
        """
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        """
        Check if the current state is terminal (hand has ended).
        
        Terminal conditions:
        - All players but one have folded
        - Showdown has occurred
        
        Returns:
            True if hand is over, False otherwise.
        """
        pass

    @abstractmethod
    def get_legal_actions(self, player: AbstractPlayer) -> List[Tuple[str, int]]:
        """
        Get list of legal actions for the specified player.
        Implements action abstraction for efficiency.
        
        Args:
            player: The player whose legal actions to determine
        
        Returns:
            List of (action, amount) tuples. Examples:
            - ('fold', 0)
            - ('check', 0)
            - ('call', 0)
            - ('raise', 100)  # Raise to total of 100
        
        Action abstraction guidelines:
        - Limit raises to 3-4 strategic sizes (e.g., 1/3 pot, 1/2 pot, pot-sized)
        - Include all-in as an option
        - Total actions per state: 4-7 typically
        """
        pass

    @abstractmethod
    def get_remaining_deck_cards(self) -> List[str]:
        """
        Get list of cards that haven't been dealt yet.
        
        Returns:
            List of card strings (e.g., ['AS', '7H', 'QC', ...])
            Excludes:
            - Community cards
            - All players' hole cards
        
        Used for:
        - Monte Carlo hand strength simulation
        - Chance node sampling in Expectiminimax
        """
        pass

    @abstractmethod
    def apply_action(self, player: AbstractPlayer, action: str, raise_amount: int = 0):
        """
        Apply a player's action to modify the game state.
        
        Args:
            player: The player taking the action
            action: Action string ('fold', 'check', 'call', 'raise')
            raise_amount: Total bet amount for raises (not the increment)
        
        Side effects:
        - Updates player's chips and current_bet
        - Updates pot size
        - May update current_bet for the table
        - Marks player as folded if applicable
        - Updates players_acted_this_round
        """
        pass

    @abstractmethod
    def get_active_players(self) -> List[AbstractPlayer]:
        """
        Get list of players still in the hand.
        
        Returns:
            List of players who haven't folded.
        """
        pass

    @abstractmethod
    def get_current_player(self) -> AbstractPlayer:
        """
        Get the player whose turn it is.
        
        Returns:
            The player who needs to act now.
        """
        pass

    @abstractmethod
    def is_betting_round_complete(self) -> bool:
        """
        Check if current betting round is finished.
        
        Complete when:
        - All active players have acted AND
        - All active players have matched the current bet OR gone all-in
        
        Returns:
            True if ready to advance to next stage, False otherwise.
        """
        pass

    @abstractmethod
    def advance_stage(self):
        """
        Move to the next stage of the hand and deal community cards.
        
        Stage progression:
        - preflop → flop (deal 3 cards)
        - flop → turn (deal 1 card)
        - turn → river (deal 1 card)
        - river → showdown
        
        Side effects:
        - Updates community_cards
        - Updates betting_round
        - Resets current_bet to 0
        - Resets all players' current_bet to 0
        - Clears players_acted_this_round
        """
        pass

    @abstractmethod
    def get_pot_size(self) -> int:
        """Get the current pot size."""
        pass

    @abstractmethod
    def get_current_bet(self) -> int:
        """Get the current bet amount that needs to be matched."""
        pass

    @abstractmethod
    def get_community_cards(self) -> List[str]:
        """Get the current community cards on the board."""
        pass


#------6. Monte Carlo Utilities (Helper - Not Required to Implement)------

class MonteCarloHelper:
    """
    Optional helper class for Monte Carlo simulation.
    Not required to implement - provided as guidance.
    """
    
    @staticmethod
    def simulate_hand_strength(
        ai_hole_cards: List[str],
        community_cards: List[str],
        remaining_deck: List[str],
        num_simulations: int = 500
    ) -> float:
        """
        Estimate win probability through Monte Carlo simulation.
        
        Args:
            ai_hole_cards: AI's 2 hole cards
            community_cards: Current board (0-5 cards)
            remaining_deck: Cards not yet dealt
            num_simulations: Number of random simulations to run
        
        Returns:
            Win probability (0.0 to 1.0)
        
        Algorithm:
        1. For each simulation:
           - Complete the board randomly (if needed)
           - Deal random opponent cards
           - Evaluate both hands
           - Count wins/ties
        2. Return (wins + 0.5 * ties) / total_simulations
        """
        pass
    
    @staticmethod
    def evaluate_state_heuristic(
        game_state,
        ai_player: AbstractPlayer
    ) -> float:
        """
        Evaluate non-terminal game state.
        
        Combines multiple factors:
        - Hand strength (via Monte Carlo)
        - Pot size
        - Cost to continue
        - Position
        - Stack depth
        
        Returns:
            Expected value in chips
        """
        pass