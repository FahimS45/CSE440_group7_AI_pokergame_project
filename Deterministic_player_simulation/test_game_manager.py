"""
Game Manager for Texas Hold'em Poker.
FIXED: Uses ExpectiminimaxAgent and Player correctly.
"""

# Minimal change: Adjusted imports to match your project's 'test_' structure
from test_game_state import TexasHoldemGameState
from test_expectiminimax import ExpectiminimaxAgent
from test_playerlogic import Player # Assumed location for Player class
from typing import List

class PokerGameManager:
    """
    Manages a Texas Hold'em poker game session.
    """
    
    def __init__(self, player_names: List[str], ai_players: List[int] = [0],
                 starting_chips: int = 1000, small_blind: int = 10, big_blind: int = 20):
        """
        Initialize poker game
        
        Args:
            player_names: List of player names
            ai_players: List of indices that should be AI (e.g., [0])
            starting_chips: Starting chip count
            small_blind: Small blind amount
            big_blind: Big blind amount
        """

        self.players = []
        for i, name in enumerate(player_names):
            if i in ai_players:
                self.players.append(
                    # Using search_depth=3 from the GitHub code
                    ExpectiminimaxAgent(name, starting_chips, search_depth=3)
                )
            else:
                self.players.append(Player(name, starting_chips))
        
        self.game_state = TexasHoldemGameState(self.players, small_blind, big_blind)
        self.hand_number = 0
    
    def play_hand(self, verbose: bool = True):
        """
        Play a single hand of poker.
        
        Args:
            verbose: Whether to print game updates
        """
        self.hand_number += 1
        
        if verbose:
            print("\n" + "="*60)
            print(f"HAND #{self.hand_number}")
            print("="*60)
            self._print_game_status()
        
        # Play through all betting rounds
        for betting_round in ["preflop", "flop", "turn", "river"]:
            if verbose:
                print(f"\n--- {betting_round.upper()} ---")
                if betting_round != "preflop":
                    print(f"Community cards: {self.game_state.community_cards}")
            
            # Play betting round
            self._play_betting_round(verbose)
            
            # Check if hand is over (only one player left)
            active_players = self.game_state.get_active_players()
            if len(active_players) <= 1:
                if verbose:
                    print(f"\nAll players folded except {active_players[0].name}")
                break
            
            # Advance to next stage (deal community cards)
            if betting_round != "river":
                self.game_state.advance_stage()
        
        # Showdown
        if verbose:
            print("\n--- SHOWDOWN ---")
            self._print_showdown()
        
        winners = self.game_state.determine_winner()
        
        if verbose:
            print("\n--- RESULTS ---")
            for winner, amount in winners:
                print(f"{winner.name} wins {amount} chips!")
            self._print_game_status()
    
    
    def _play_betting_round(self, verbose: bool = True):
        """ Play through one betting round"""
        
        safety_counter = 0
        max_actions = 50
        
        while not self.game_state.is_betting_round_complete():
            safety_counter += 1
            
            if safety_counter > max_actions:
                if verbose:
                    print(f"\n⚠️ SAFETY STOP: Too many actions!")
                break
            
            # Check if only one player can act
            active_with_chips = [p for p in self.game_state.get_active_players() if p.chips > 0]
            if len(active_with_chips) <= 1:
                if verbose:
                    print(f"\n✓ Betting complete: Only {len(active_with_chips)} player(s) with chips")
                break
            
            current_player = self.game_state.get_current_player()
            
            # Skip if player has no chips
            if current_player.chips == 0:
                if verbose:
                    print(f"{current_player.name} is all-in, skipping")
                self.game_state.next_player()
                continue
            
            if verbose:
                self._print_player_turn(current_player)
            
            # ✅ Handles AI vs AI, Human vs AI, Deterministic vs AI
            if isinstance(current_player, ExpectiminimaxAgent):
                action_result = current_player.make_decision(self.game_state)
            else:
                # Passes a simplified dict for non-AI players like HumanPlayer or Deterministic opponents
                game_state_dict = self.game_state.get_game_state_dict()
                action_result = current_player.make_decision(game_state_dict)
            
            # ✅ Handle both tuple and string returns
            if isinstance(action_result, tuple):
                action, amount = action_result
            else:
                action = action_result
                amount = 0
            
            # Handle actions
            if action == "fold":
                self.game_state.apply_action(current_player, "fold")
                if verbose:
                    print(f"{current_player.name} folds")
            
            elif action == "check":
                to_call = self.game_state.current_bet - current_player.current_bet
                
                # Check is implicitly a call if there's a bet to match
                if to_call > 0 and current_player.chips >= to_call:
                    action = "call" # Coerce to call before applying
                    self.game_state.apply_action(current_player, action)
                    if verbose:
                        print(f"{current_player.name} calls {to_call} (auto-call/check)")
                elif to_call > 0 and current_player.chips < to_call:
                    action = "call" # Coerce to all-in call
                    self.game_state.apply_action(current_player, action)
                    if verbose:
                        print(f"{current_player.name} calls All-In ({current_player.chips}) (auto-call/check)")
                elif to_call == 0:
                    self.game_state.apply_action(current_player, action)
                    if verbose:
                        print(f"{current_player.name} checks")
                else:
                    # Case for a player trying to check when they should call/fold (shouldn't happen with valid logic)
                    self.game_state.apply_action(current_player, "check")
                    if verbose:
                         print(f"{current_player.name} checks")


            elif action == "call":
                to_call = self.game_state.current_bet - current_player.current_bet
                self.game_state.apply_action(current_player, "call")
                if verbose:
                    print(f"{current_player.name} calls {to_call}")
            
            elif action == "raise":
                try:
                    self.game_state.apply_action(current_player, "raise", amount)
                    if verbose:
                        print(f"{current_player.name} raises to {amount}")
                except ValueError as e:
                    # If raise fails, fall back to call/check
                    if verbose:
                        print(f"⚠️ Raise failed: {e}")
                    to_call = self.game_state.current_bet - current_player.current_bet
                    if to_call > 0:
                        self.game_state.apply_action(current_player, "call")
                        if verbose:
                            print(f"{current_player.name} calls {to_call} instead")
                    else:
                        self.game_state.apply_action(current_player, "check")
                        if verbose:
                            print(f"{current_player.name} checks instead")
            
            # Move to next player
            self.game_state.next_player()
            
            # Safety check (if all players but one are folded/all-in)
            num_active_or_allin = len([p for p in self.game_state.players if not p.folded and p.chips > 0])
            if num_active_or_allin <= 1 and self.game_state.is_betting_round_complete():
                break
    
    def _print_game_status(self):
        """Print current game status"""
        print("\nChip counts:")
        for player in self.players:
            status = "FOLDED" if player.folded else f"{player.chips} chips"
            print(f"  {player.name}: {status}")
        print(f"Pot: {self.game_state.pot}")
    
    def _print_player_turn(self, player: Player):
        """Print player's turn information"""
        to_call = self.game_state.current_bet - player.current_bet
        
        print(f"\n{player.name}'s turn:")
        print(f"  Hole cards: {player.cards}")
        print(f"  Chips: {player.chips}")
        print(f"  Current bet: {player.current_bet}")
        print(f"  To call: {to_call}")
        print(f"  Pot: {self.game_state.pot}")
    
    def _print_showdown(self):
        """Print showdown information"""
        print(f"Community cards: {self.game_state.community_cards}")
        print("\nPlayer hands:")
        
        for player in self.game_state.get_active_players():
            full_hand = player.cards + self.game_state.community_cards
            
            # Assuming self.game_state.evaluator exists and is available
            # It is initialized in TexasHoldemGameState
            hand_eval = self.game_state.evaluator.evaluate_hand(full_hand) 
            
            print(f"  {player.name}: {player.cards} -> Rank: {hand_eval[0]}, Tiebreakers: {hand_eval[1]}")
    
    def play_tournament(self, num_hands: int = 10, verbose: bool = True):
        """
        Play multiple hands.
        
        Args:
            num_hands: Number of hands to play
            verbose: Whether to print game updates
        """
        for _ in range(num_hands):
            # Check if any players are out
            active_players = [p for p in self.players if p.chips > 0]
            if len(active_players) <= 1:
                if verbose:
                    print("\n" + "="*60)
                    print("TOURNAMENT OVER")
                    if active_players:
                        print(f"Winner: {active_players[0].name}")
                    print("="*60)
                break
            
            # Play hand
            self.play_hand(verbose)
            
            # Start new round
            self.game_state.reset_round()
        
        # Final standings
        if verbose:
            print("\n" + "="*60)
            print("FINAL STANDINGS")
            print("="*60)
            sorted_players = sorted(self.players, key=lambda p: p.chips, reverse=True)
            for i, player in enumerate(sorted_players, 1):
                print(f"{i}. {player.name}: {player.chips} chips")