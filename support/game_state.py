"""
GameState implementation for Texas Hold'em poker.
Clean implementation with List[str] throughout - no conversions needed!
"""

from abstracts import AbstractGameState, AbstractPlayer
from cardsystem import Deck
from hand_evaluator import PokerHandEvaluator
from typing import List, Tuple

class TexasHoldemGameState(AbstractGameState):
    """
    Manages the state of a Texas Hold'em poker game.
    """
    
    def __init__(self, players: List[AbstractPlayer], small_blind: int = 10, big_blind: int = 20):
        """
        Initialize Texas Hold'em game state.
        
        Args:
            players: List of players (2-10 players)
            small_blind: Small blind amount
            big_blind: Big blind amount
        """
        if len(players) < 2:
            raise ValueError("Need at least 2 players")
        if len(players) > 10:
            raise ValueError("Maximum 10 players allowed")
        
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        # Deck and cards
        self.deck = Deck()
        self.community_cards = []  # List[str] - directly from deck
        
        # Game state tracking
        self.pot = 0
        self.current_bet = 0
        self.button_position = 0  # Dealer button
        self.current_player_index = 0
        
        # Betting round tracking
        self.betting_round = "preflop"  # preflop, flop, turn, river, showdown
        self.players_acted_this_round = set()  # Track who has acted
        
        # Hand evaluator
        self.evaluator = PokerHandEvaluator()
        
        # Initialize first hand
        self.reset_round()
    
    def reset_round(self):
        """Start a new hand"""
        # Reset deck
        self.deck.reset()
        self.deck.shuffle()
        
        # Reset community cards
        self.community_cards = []
        
        # Reset pot and bets
        self.pot = 0
        self.current_bet = 0
        
        # Reset all players
        for player in self.players:
            player.reset_hand()
        
        # Move button clockwise
        self.button_position = (self.button_position + 1) % len(self.players)
        
        # Post blinds
        self._post_blinds()
        
        # Deal hole cards (2 to each player)
        self._deal_hole_cards()
        
        # Betting starts left of big blind
        self.current_player_index = (self.button_position + 3) % len(self.players)
        self.betting_round = "preflop"
        self.players_acted_this_round = set()
    
    def _post_blinds(self):
        """Post small and big blinds"""
        num_players = len(self.players)
        
        # Small blind (left of button)
        sb_position = (self.button_position + 1) % num_players
        sb_player = self.players[sb_position]
        sb_amount = min(self.small_blind, sb_player.chips)
        sb_player.update_stack(-sb_amount)
        sb_player.current_bet = sb_amount
        self.pot += sb_amount
        
        # Big blind (left of small blind)
        bb_position = (self.button_position + 2) % num_players
        bb_player = self.players[bb_position]
        bb_amount = min(self.big_blind, bb_player.chips)
        bb_player.update_stack(-bb_amount)
        bb_player.current_bet = bb_amount
        self.pot += bb_amount
        
        # Set current bet to big blind
        self.current_bet = bb_amount
    
    def _deal_hole_cards(self):
        """Deal 2 cards to each player"""
        for player in self.players:
            # Deck.deal() now returns List[str] directly!
            player.cards = self.deck.deal(2)
    
    def get_current_player(self) -> AbstractPlayer:
        """Return the player whose turn it is"""
        return self.players[self.current_player_index]
    
    def get_active_players(self) -> List[AbstractPlayer]:
        """Return players who haven't folded"""
        return [p for p in self.players if not p.folded]
    
    def get_community_cards(self) -> List[str]:
        """Return community cards"""
        return self.community_cards
    
    def get_pot_size(self) -> int:
        """Return current pot size"""
        return self.pot
    
    def get_current_bet(self) -> int:
        """Return the current bet to call"""
        return self.current_bet
    
    def apply_action(self, player: AbstractPlayer, action: str, raise_amount: int = 0):
        """
        Apply a player's action to the game state.
        
        Args:
            player: The player taking action
            action: 'fold', 'check', 'call', 'raise'
            raise_amount: Total amount for raise (not just the increment)
        """
        if action == "fold":
            player.folded = True
        
        elif action == "check":
            # Can only check if no bet to call
            if self.current_bet > player.current_bet:
                raise ValueError(f"{player.name} cannot check, must call or fold")
        
        elif action == "call":
            # Call the current bet
            to_call = self.current_bet - player.current_bet
            actual_call = min(to_call, player.chips)
            
            player.update_stack(-actual_call)
            player.current_bet += actual_call
            self.pot += actual_call
        
        elif action == "raise":
            # Raise to raise_amount
            if raise_amount <= self.current_bet:
                raise ValueError(f"Raise amount must be greater than current bet {self.current_bet}")
            
            to_bet = raise_amount - player.current_bet
            actual_bet = min(to_bet, player.chips)
            
            player.update_stack(-actual_bet)
            player.current_bet += actual_bet
            self.pot += actual_bet
            
            # Update current bet
            self.current_bet = player.current_bet
            
            # Reset players_acted since there's a new bet
            self.players_acted_this_round = {player}
        
        else:
            raise ValueError(f"Unknown action: {action}")
        
        # Mark player as acted
        self.players_acted_this_round.add(player)
    
    def next_player(self):
        """Advance to next active player"""
        original_index = self.current_player_index
        
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            
            # Don't cycle forever
            if self.current_player_index == original_index:
                break
            
            current_player = self.players[self.current_player_index]
            
            # Skip if folded or all-in
            if not current_player.folded and current_player.chips > 0:
                break
    
    def is_betting_round_complete(self) -> bool:
        """
        Check if betting round is complete.
        Complete when all active players have acted and matched the current bet.
        """
        active_players = self.get_active_players()
        
        # If only one player left, round is over
        if len(active_players) <= 1:
            return True
        
        # Check if all active players have acted
        for player in active_players:
            if player not in self.players_acted_this_round:
                return False
            
            # Check if they've matched the bet (or are all-in)
            if player.current_bet < self.current_bet and player.chips > 0:
                return False
        
        return True
    
    def advance_stage(self):
        """Move to next stage and deal community cards"""
        # Reset for new betting round
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
        self.players_acted_this_round = set()
        
        # Deal community cards based on stage
        if self.betting_round == "preflop":
            # Deal flop (3 cards) - deck.deal() returns List[str] directly!
            self.community_cards = self.deck.deal(3)
            self.betting_round = "flop"
        
        elif self.betting_round == "flop":
            # Deal turn (1 card)
            self.community_cards.extend(self.deck.deal(1))
            self.betting_round = "turn"
        
        elif self.betting_round == "turn":
            # Deal river (1 card)
            self.community_cards.extend(self.deck.deal(1))
            self.betting_round = "river"
        
        elif self.betting_round == "river":
            # Go to showdown
            self.betting_round = "showdown"
        
        # Betting starts left of button (or first active player)
        self.current_player_index = (self.button_position + 1) % len(self.players)
        while self.players[self.current_player_index].folded:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def determine_winner(self) -> List[Tuple[AbstractPlayer, int]]:
        """
        Determine winner(s) at showdown.
        Returns list of (player, amount_won) tuples.
        
        Note: This is simplified and doesn't handle side pots properly.
        """
        active_players = self.get_active_players()
        
        if len(active_players) == 1:
            # Only one player left, they win
            winner = active_players[0]
            winner.update_stack(self.pot)
            return [(winner, self.pot)]
        
        # Evaluate all hands
        best_hand = None
        winners = []
        
        for player in active_players:
            # Player.cards is List[str], community_cards is List[str]
            # Perfect! No conversion needed!
            full_hand = player.cards + self.community_cards
            
            if best_hand is None:
                best_hand = full_hand
                winners = [player]
            else:
                comparison = self.evaluator.compare_hands(full_hand, best_hand)
                
                if comparison == 1:
                    # New winner
                    best_hand = full_hand
                    winners = [player]
                elif comparison == 0:
                    # Tie
                    winners.append(player)
        
        # Split pot among winners
        pot_share = self.pot // len(winners)
        results = []
        
        for winner in winners:
            winner.update_stack(pot_share)
            results.append((winner, pot_share))
        
        return results
    
    def get_game_state_dict(self):
        """Return game state as dictionary for player decision making"""
        return {
            "pot": self.pot,
            "current_bet": self.current_bet,
            "community_cards": self.community_cards,
            "betting_round": self.betting_round,
            "active_players": len(self.get_active_players())
        }