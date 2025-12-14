"""
GameState implementation for Texas Hold'em poker.
"""

import copy 
from typing import List, Tuple
from support.abstracts import AbstractGameState, AbstractPlayer
from support.cardsystem import Deck 
from support.hand_evaluator import PokerHandEvaluator 

class TexasHoldemGameState(AbstractGameState):
    """
    Manages the state of a Texas Hold'em poker game.
    """
    
    def __init__(self, players: List[AbstractPlayer], small_blind: int = 10, big_blind: int = 20):
        if len(players) < 2:
            raise ValueError("Need at least 2 players")
        if len(players) > 10:
            raise ValueError("Maximum 10 players allowed")
        
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        self.deck = Deck()
        self.community_cards = []
        
        self.pot = 0
        self.current_bet = 0
        self.button_position = 0
        self.current_player_index = 0
        
        self.betting_round = "preflop"
        self.players_acted_this_round = set()
        
        self.evaluator = PokerHandEvaluator()
        
        self.reset_round()
    
    def reset_round(self):
        """Start a new hand"""
        self.deck.reset()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        
        for player in self.players:
            player.reset_hand()
        
        self.button_position = (self.button_position + 1) % len(self.players)
        self._post_blinds()
        self._deal_hole_cards()
        
        self.current_player_index = (self.button_position + 3) % len(self.players)
        self.betting_round = "preflop"
        self.players_acted_this_round = set()
    
    def _post_blinds(self):
        """Post small and big blinds"""
        num_players = len(self.players)
        
        sb_position = (self.button_position + 1) % num_players
        sb_player = self.players[sb_position]
        sb_amount = min(self.small_blind, sb_player.chips)
        sb_player.update_stack(-sb_amount)
        sb_player.current_bet = sb_amount
        self.pot += sb_amount
        
        bb_position = (self.button_position + 2) % num_players
        bb_player = self.players[bb_position]
        bb_amount = min(self.big_blind, bb_player.chips)
        bb_player.update_stack(-bb_amount)
        bb_player.current_bet = bb_amount
        self.pot += bb_amount
        
        self.current_bet = bb_amount
    
    def _deal_hole_cards(self):
        """Deal 2 cards to each player"""
        for player in self.players:
            player.cards = self.deck.deal(2)
    
    def get_current_player(self) -> AbstractPlayer:
        return self.players[self.current_player_index]
    
    def get_active_players(self) -> List[AbstractPlayer]:
        return [p for p in self.players if not p.folded]
    
    def get_community_cards(self) -> List[str]:
        return self.community_cards
    
    def get_pot_size(self) -> int:
        return self.pot
    
    def get_current_bet(self) -> int:
        return self.current_bet
    
    def apply_action(self, player: AbstractPlayer, action: str, raise_amount: int = 0):
        """Apply a player's action to game state safely"""
        
        if action == "fold":
            player.folded = True
            self.players_acted_this_round.add(player)

        elif action == "check":
            to_call = self.current_bet - player.current_bet
            if to_call > 0:
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
            # Limit raise to player’s chips and total chips in play
            max_raise = player.chips + player.current_bet
            safe_raise = min(raise_amount, max_raise)
            
            if safe_raise <= self.current_bet:
                # Cannot raise below current bet
                safe_raise = self.current_bet + min(self.big_blind, player.chips)
            
            to_bet = safe_raise - player.current_bet
            actual_bet = min(to_bet, player.chips)
            
            player.update_stack(-actual_bet)
            player.current_bet += actual_bet
            self.pot += actual_bet
            
            self.current_bet = max(self.current_bet, player.current_bet)
            self.players_acted_this_round = set([player])
        
        else:
            raise ValueError(f"Unknown action: {action}")
        
        # Safety check: pot cannot exceed total chips
        total_chips = sum(p.chips + p.current_bet for p in self.players)
        if self.pot > total_chips:
            self.pot = total_chips
    
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
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
        self.players_acted_this_round = set()
        
        if self.betting_round == "preflop":
            self.community_cards = self.deck.deal(3)
            self.betting_round = "flop"
        elif self.betting_round == "flop":
            self.community_cards.extend(self.deck.deal(1))
            self.betting_round = "turn"
        elif self.betting_round == "turn":
            self.community_cards.extend(self.deck.deal(1))
            self.betting_round = "river"
        elif self.betting_round == "river":
            self.betting_round = "showdown"
        
        self.current_player_index = (self.button_position + 1) % len(self.players)
        while self.players[self.current_player_index].folded:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def determine_winner(self) -> List[Tuple[AbstractPlayer, int]]:
        """
        Determine winner(s) at showdown with CORRECT pot distribution
        
        ✅ FIXES:
        1. Store pot BEFORE clearing it (for correct return value)
        2. Handle fold scenario correctly
        3. Proper hand comparison
        """
        
        active_players = self.get_active_players()
        
        # Edge case: everyone folded (shouldn't happen but be safe)
        if len(active_players) == 0:
            return []
        
        # ✅ FIX: Store pot BEFORE awarding it
        pot_to_award = self.pot
        
        # Single player wins (opponent folded)
        if len(active_players) == 1:
            winner = active_players[0]
            winner.update_stack(pot_to_award)
            self.pot = 0  # Clear pot after awarding
            return [(winner, pot_to_award)]  # ✅ Return correct amount
        
        # Multiple players - evaluate hands
        best_rank = None
        best_tiebreakers = None
        winners = []
        
        for player in active_players:
            full_hand = player.cards + self.community_cards
            rank, tiebreakers = self.evaluator.evaluate_hand(full_hand)
            
            if best_rank is None:
                best_rank = rank
                best_tiebreakers = tiebreakers
                winners = [player]
            else:
                # Higher rank = better hand
                if rank > best_rank:
                    best_rank = rank
                    best_tiebreakers = tiebreakers
                    winners = [player]
                elif rank == best_rank:
                    # Same rank, check tiebreakers
                    tie_result = self._compare_tiebreakers(tiebreakers, best_tiebreakers)
                    if tie_result > 0:
                        best_tiebreakers = tiebreakers
                        winners = [player]
                    elif tie_result == 0:
                        winners.append(player)
        
        # Split pot among winners
        pot_share = pot_to_award // len(winners)
        results = []
        
        for winner in winners:
            winner.update_stack(pot_share)
            results.append((winner, pot_share))
        
        # Clear pot
        self.pot = 0
        
        return results


    def _compare_tiebreakers(self, tb1: List[int], tb2: List[int]) -> int:
        """
        Compare tiebreaker lists
        
        Returns:
            1 if tb1 > tb2
            -1 if tb1 < tb2
            0 if equal
        """
        for i in range(min(len(tb1), len(tb2))):
            if tb1[i] > tb2[i]:
                return 1
            elif tb1[i] < tb2[i]:
                return -1
        return 0
    
    def get_game_state_dict(self):
        """Return game state as dictionary"""
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
        """Generate safe legal actions"""
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
        
        # RAISE (single safe raise)
        if player.chips > to_call:
            raise_amount = player.current_bet + min(player.chips, max(self.big_blind, pot))
            chips_needed = raise_amount - player.current_bet
            if chips_needed > 0 and player.chips >= chips_needed:
                actions.append(('raise', raise_amount))
        
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