"""
GameState implementation for Texas Hold'em poker.
Clean implementation
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
            players: List of players 
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
        self.community_cards = []  
        
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
        """Apply a player's action to game state"""
        
        if action == "fold":
            player.folded = True
            self.players_acted_this_round.add(player)

        elif action == "check":
            to_call = self.current_bet - player.current_bet
            if to_call > 0:
                # Auto-convert to call
                actual_call = min(to_call, player.chips)
                player.update_stack(-actual_call)
                player.current_bet += actual_call
                self.pot += actual_call
            self.players_acted_this_round.add(player)

        elif action == "call":
            to_call = self.current_bet - player.current_bet
            actual_call = min(to_call, player.chips)
            player.update_stack(-actual_call)
            player.current_bet += actual_call
            self.pot += actual_call
            self.players_acted_this_round.add(player)

        elif action == "raise":
            if raise_amount <= self.current_bet:
                raise ValueError(f"Raise amount must be greater than current bet {self.current_bet}")

            to_bet = raise_amount - player.current_bet
            actual_bet = min(to_bet, player.chips)

            player.update_stack(-actual_bet)
            player.current_bet += actual_bet
            self.pot += actual_bet

            self.current_bet = player.current_bet
            self.players_acted_this_round = set([player])
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def next_player(self):
        """Advance to next active player"""
        original_index = self.current_player_index
        attempts = 0
        max_attempts = len(self.players) + 1
        
        while attempts < max_attempts:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            attempts += 1
            
            if self.current_player_index == original_index and attempts > 1:
                break
            
            current_player = self.players[self.current_player_index]
            
            if not current_player.folded and current_player.chips > 0:
                break
        
        if attempts >= max_attempts:
            for p in self.players:
                self.players_acted_this_round.add(p)

    def is_betting_round_complete(self) -> bool:
        """Check if betting round is complete"""
        active_players = self.get_active_players()
        
        if len(active_players) <= 1:
            return True
        
        players_who_can_act = [p for p in active_players if p.chips > 0]
        
        if len(players_who_can_act) <= 1:
            return True
        
        for player in active_players:
            if player.chips == 0:
                continue
                
            if player not in self.players_acted_this_round:
                return False
            
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
        """Determine winner(s) at showdown"""
        active_players = self.get_active_players()
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.update_stack(self.pot)
            return [(winner, self.pot)]
        
        best_hand = None
        winners = []
        
        for player in active_players:
            full_hand = player.cards + self.community_cards
            
            if best_hand is None:
                best_hand = full_hand
                winners = [player]
            else:
                comparison = self.evaluator.compare_hands(full_hand, best_hand)
                
                if comparison == 1:
                    best_hand = full_hand
                    winners = [player]
                elif comparison == 0:
                    winners.append(player)
        
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
    
    def clone(self):
        """Create deep copy for tree search"""
        return copy.deepcopy(self)
    
    def is_terminal(self):
        """Check if hand is over"""
        active = self.get_active_players()
        return len(active) <= 1 or self.betting_round == "showdown"
    
    def get_legal_actions(self, player):
        """
        FIXED RAISE VERSION: Only 1 raise size (pot-sized)
        Best for deep Expectiminimax search (depth 4+)
        
        Actions: fold, check, call, raise (pot)
        Branching factor: ~3-4 per node
        """
        actions = []
        
        to_call = self.current_bet - player.current_bet
        pot = self.pot
        
        # FOLD
        if to_call > 0:
            actions.append(('fold', 0))
        
        # CHECK
        if to_call == 0:
            actions.append(('check', 0))
        
        # CALL
        if to_call > 0 and player.chips > 0:
            actions.append(('call', 0))
        
        # RAISE (single pot-sized bet)
        if player.chips > to_call:
            raise_amount = self.current_bet + max(self.big_blind, pot)
            chips_needed = raise_amount - player.current_bet
            
            if chips_needed > 0 and player.chips >= chips_needed:
                actions.append(('raise', raise_amount))
        
        # Safety
        if len(actions) == 0:
            actions.append(('check', 0))
        
        return actions
    
    def get_remaining_deck_cards(self):
        """Return list of cards not yet dealt"""
        all_cards = []
        for suit in ['H', 'D', 'C', 'S']:
            for rank in ['2','3','4','5','6','7','8','9','10','J','Q','K','A']:
                all_cards.append(rank + suit)
        
        known_cards = set(self.community_cards)
        for player in self.players:
            known_cards.update(player.cards)
        
        return [c for c in all_cards if c not in known_cards]