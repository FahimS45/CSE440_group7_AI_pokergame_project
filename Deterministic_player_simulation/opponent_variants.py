"""
Different opponent player types for testing AI performance.
FIXED: Non-AI players can now return tuples for raises
"""

from Deterministic_player_simulation.abstracts import AbstractPlayer
import random


class CallingStationPlayer(AbstractPlayer):
    """
    Always calls, never folds (unless broke), never raises.
    Classic "fish" player - most exploitable.
    """
    
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
    
    def make_decision(self, game_state):
        """Always tries to call/check - returns string"""
        if isinstance(game_state, dict):
            to_call = game_state.get("current_bet", 0) - self.current_bet
        else:
            to_call = game_state.get_current_bet() - self.current_bet
        
        if to_call > 0:
            if self.chips >= to_call:
                return "call"
            else:
                return "fold"
        else:
            return "check"
    
    def update_stack(self, amount: int):
        self.chips += amount
    
    def reset_hand(self):
        self.cards = []
        self.current_bet = 0
        self.folded = False


class AggressivePlayer(AbstractPlayer):
    """
    ✅ FIXED: Always bets/raises when possible
    Now returns tuple (action, amount) for raises
    """
    
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
    
    def make_decision(self, game_state):
        """
        ✅ FIXED: Returns tuple for raises, string for other actions
        """
        if isinstance(game_state, dict):
            to_call = game_state.get("current_bet", 0) - self.current_bet
            pot = game_state.get("pot", 100)
            current_bet = game_state.get("current_bet", 0)
        else:
            to_call = game_state.get_current_bet() - self.current_bet
            pot = game_state.get_pot_size()
            current_bet = game_state.get_current_bet()
        
        # Calculate raise amount (fixed $20 raise like AI)
        raise_amount = current_bet + 20
        chips_needed = raise_amount - self.current_bet
        
        # Try to raise if we have enough chips
        if self.chips >= chips_needed and chips_needed > 0:
            return ('raise', raise_amount)  # ✅ Return tuple
        elif to_call > 0 and self.chips >= to_call:
            return "call"
        elif to_call == 0:
            return "check"
        else:
            return "fold"
    
    def update_stack(self, amount: int):
        self.chips += amount
    
    def reset_hand(self):
        self.cards = []
        self.current_bet = 0
        self.folded = False


class TightPlayer(AbstractPlayer):
    """
    Folds frequently, only calls small bets.
    Plays very conservatively - minimizes losses.
    """
    
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
        self.fold_threshold = 0.4  # Folds if bet > 40% of pot
    
    def make_decision(self, game_state):
        """Folds often, only calls small bets"""
        if isinstance(game_state, dict):
            to_call = game_state.get("current_bet", 0) - self.current_bet
            pot = game_state.get("pot", 100)
        else:
            to_call = game_state.get_current_bet() - self.current_bet
            pot = game_state.get_pot_size()
        
        # Fold if bet is too large relative to pot
        if to_call > pot * self.fold_threshold:
            return "fold"
        elif to_call > 0:
            return "call" if self.chips >= to_call else "fold"
        else:
            return "check"
    
    def update_stack(self, amount: int):
        self.chips += amount
    
    def reset_hand(self):
        self.cards = []
        self.current_bet = 0
        self.folded = False


class RandomPlayer(AbstractPlayer):
    """
    ✅ FIXED: Makes random decisions including raises
    Now returns tuple for raises
    """
    
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
    
    def make_decision(self, game_state):
        """
        ✅ FIXED: Randomly chooses from legal actions
        Returns tuple for raises, string for other actions
        """
        if isinstance(game_state, dict):
            to_call = game_state.get("current_bet", 0) - self.current_bet
            current_bet = game_state.get("current_bet", 0)
        else:
            to_call = game_state.get_current_bet() - self.current_bet
            current_bet = game_state.get_current_bet()
        
        if to_call > 0:
            # Can fold, call, or raise
            if self.chips < to_call:
                return "fold"
            
            choice = random.choice(["fold", "call", "raise"])
            
            if choice == "raise":
                # Calculate raise amount (fixed $20 raise)
                raise_amount = current_bet + 20
                chips_needed = raise_amount - self.current_bet
                
                if self.chips >= chips_needed:
                    return ('raise', raise_amount)  # ✅ Return tuple
                else:
                    return "call"  # Not enough chips, just call
            else:
                return choice
        else:
            # Can check or raise
            choice = random.choice(["check", "raise"])
            
            if choice == "raise":
                # Calculate raise amount (fixed $20 raise)
                raise_amount = current_bet + 20
                chips_needed = raise_amount - self.current_bet
                
                if self.chips >= chips_needed:
                    return ('raise', raise_amount)  # ✅ Return tuple
                else:
                    return "check"  # Not enough chips, just check
            else:
                return choice
    
    def update_stack(self, amount: int):
        self.chips += amount
    
    def reset_hand(self):
        self.cards = []
        self.current_bet = 0
        self.folded = False


class PassivePlayer(AbstractPlayer):
    """
    Never raises, only checks/calls/folds.
    Like calling station but will fold to large bets.
    """
    
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
        self.fold_threshold = 0.8  # Folds if bet > 80% of pot
    
    def make_decision(self, game_state):
        """Never raises, folds to large bets"""
        if isinstance(game_state, dict):
            to_call = game_state.get("current_bet", 0) - self.current_bet
            pot = game_state.get("pot", 100)
        else:
            to_call = game_state.get_current_bet() - self.current_bet
            pot = game_state.get_pot_size()
        
        if to_call > pot * self.fold_threshold:
            return "fold"
        elif to_call > 0:
            return "call" if self.chips >= to_call else "fold"
        else:
            return "check"
    
    def update_stack(self, amount: int):
        self.chips += amount
    
    def reset_hand(self):
        self.cards = []
        self.current_bet = 0
        self.folded = False