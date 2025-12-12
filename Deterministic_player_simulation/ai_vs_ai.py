"""
AI vs AI Poker Demo
Two Expectiminimax agents competing against each other
"""

from Deterministic_player_simulation.game_manager import PokerGameManager
from Deterministic_player_simulation.expectiminimax import ExpectiminimaxAgent
from Deterministic_player_simulation.game_state import TexasHoldemGameState
import time


class ai_vs_ai:
    """
    Demo class for AI vs AI poker matches
    """
    
    def __init__(self, starting_chips=1000, small_blind=10, big_blind=20):
        """
        Initialize AI vs AI game
        
        Args:
            starting_chips: Starting chip count for each AI
            small_blind: Small blind amount
            big_blind: Big blind amount
        """
        self.starting_chips = starting_chips
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        # Create two AI agents with different search depths for variety
        self.ai1 = ExpectiminimaxAgent(
            name="AI_Agent_1",
            chips=starting_chips,
            search_depth=3  # Slightly deeper search
        )
        
        self.ai2 = ExpectiminimaxAgent(
            name="AI_Agent_2", 
            chips=starting_chips,
            search_depth=2  # Slightly shallower search
        )
        
        # Initialize game state
        self.players = [self.ai1, self.ai2]
        self.game_state = TexasHoldemGameState(
            self.players,
            small_blind=small_blind,
            big_blind=big_blind
        )
        
        self.hand_number = 0
        self.match_stats = {
            'ai1_wins': 0,
            'ai2_wins': 0,
            'ai1_total_profit': 0,
            'ai2_total_profit': 0
        }
    
    def play_single_hand(self, verbose=True):
        """
        Play a single hand between the two AIs
        
        Args:
            verbose: If True, print detailed action log
        """
        self.hand_number += 1
        
        if verbose:
            print("\n" + "="*70)
            print(f"HAND #{self.hand_number}")
            print("="*70)
            self._print_game_status()
        
        # Track chips before hand
        ai1_chips_before = self.ai1.chips
        ai2_chips_before = self.ai2.chips
        
        # Play through all betting rounds
        for betting_round in ["preflop", "flop", "turn", "river"]:
            if verbose:
                print(f"\n--- {betting_round.upper()} ---")
                if betting_round != "preflop":
                    print(f"Community cards: {self.game_state.community_cards}")
            
            self._play_betting_round(verbose)
            
            # Check if hand ended early (someone folded)
            active_players = self.game_state.get_active_players()
            if len(active_players) <= 1:
                if verbose:
                    print(f"\n🏳️ {active_players[0].name} wins - opponent folded!")
                break
            
            # Move to next stage (unless we're at river)
            if betting_round != "river":
                self.game_state.advance_stage()
        
        # Determine winner and award pot
        winners = self.game_state.determine_winner()
        
        if verbose:
            print("\n--- SHOWDOWN ---")
            self._print_showdown()
            print("\n--- RESULTS ---")
            for winner, amount in winners:
                print(f"🏆 {winner.name} wins {amount} chips!")
        
        # Update match statistics
        ai1_profit = self.ai1.chips - ai1_chips_before
        ai2_profit = self.ai2.chips - ai2_chips_before
        
        self.match_stats['ai1_total_profit'] += ai1_profit
        self.match_stats['ai2_total_profit'] += ai2_profit
        
        if ai1_profit > 0:
            self.match_stats['ai1_wins'] += 1
        elif ai2_profit > 0:
            self.match_stats['ai2_wins'] += 1
        
        if verbose:
            self._print_game_status()
    
    def _play_betting_round(self, verbose=True):
        """Play through one betting round with both AIs making decisions"""
        
        safety_counter = 0
        max_actions = 50
        
        while not self.game_state.is_betting_round_complete():
            safety_counter += 1
            
            if safety_counter > max_actions:
                if verbose:
                    print(f"\n⚠️ SAFETY STOP: Too many actions in betting round!")
                break
            
            # Check if only one player can still act
            active_with_chips = [
                p for p in self.game_state.get_active_players() 
                if p.chips > 0
            ]
            if len(active_with_chips) <= 1:
                break
            
            current_player = self.game_state.get_current_player()
            
            # Skip if player has no chips (all-in)
            if current_player.chips == 0:
                if verbose:
                    print(f"  {current_player.name} is all-in, skipping turn")
                self.game_state.next_player()
                continue
            
            if verbose:
                self._print_player_turn(current_player)
            
            # Get AI decision
            start_time = time.time()
            action_result = current_player.make_decision(self.game_state)
            decision_time = time.time() - start_time
            
            # Parse action (always tuple for our AIs)
            action, amount = action_result
            
            # Apply action
            if action == "fold":
                self.game_state.apply_action(current_player, "fold")
                if verbose:
                    print(f"  ➤ {current_player.name} folds")
            
            elif action == "check":
                self.game_state.apply_action(current_player, "check")
                to_call = self.game_state.current_bet - current_player.current_bet
                if verbose:
                    if to_call > 0:
                        print(f"  ➤ {current_player.name} calls {to_call}")
                    else:
                        print(f"  ➤ {current_player.name} checks")
            
            elif action == "call":
                to_call = self.game_state.current_bet - current_player.current_bet
                self.game_state.apply_action(current_player, "call")
                if verbose:
                    print(f"  ➤ {current_player.name} calls {to_call}")
            
            elif action == "raise":
                try:
                    self.game_state.apply_action(current_player, "raise", amount)
                    if verbose:
                        print(f"  ➤ {current_player.name} raises to {amount}")
                except ValueError as e:
                    # Fallback to call if raise fails
                    to_call = self.game_state.current_bet - current_player.current_bet
                    if to_call > 0:
                        self.game_state.apply_action(current_player, "call")
                        if verbose:
                            print(f"  ➤ {current_player.name} calls {to_call} (raise failed)")
                    else:
                        self.game_state.apply_action(current_player, "check")
                        if verbose:
                            print(f"  ➤ {current_player.name} checks (raise failed)")
            
            if verbose:
                print(f"  ⏱️ Decision time: {decision_time:.3f}s")
            
            # Move to next player
            self.game_state.next_player()
            
            # Safety check: if all but one player folded
            if all(p.folded or p.chips == 0 for p in self.game_state.players[:-1]):
                break
    
    def _print_game_status(self):
        """Print current chip counts and pot"""
        print("\n💰 Chip Counts:")
        for player in self.players:
            status = "FOLDED" if player.folded else f"{player.chips} chips"
            print(f"  {player.name}: {status}")
        print(f"  Pot: {self.game_state.pot}")
    
    def _print_player_turn(self, player):
        """Print player's current situation"""
        to_call = self.game_state.current_bet - player.current_bet
        
        print(f"\n🤖 {player.name}'s turn:")
        print(f"  Hole cards: {player.cards}")
        print(f"  Chips: {player.chips}")
        print(f"  To call: {to_call}")
        print(f"  Pot: {self.game_state.pot}")
    
    def _print_showdown(self):
        """Print final hands at showdown"""
        print(f"Community cards: {self.game_state.community_cards}")
        print("\nFinal hands:")
        
        for player in self.game_state.get_active_players():
            full_hand = player.cards + self.game_state.community_cards
            hand_eval = self.game_state.evaluator.evaluate_hand(full_hand)
            print(f"  {player.name}: {player.cards}")
            print(f"    → Rank: {hand_eval[0]}, Tiebreakers: {hand_eval[1]}")
    
    def play_match(self, num_hands=10, verbose=True):
        """
        Play multiple hands as a match
        
        Args:
            num_hands: Number of hands to play
            verbose: If True, print detailed logs
        """
        print("\n" + "="*70)
        print("AI vs AI POKER MATCH")
        print("="*70)
        print(f"Match: {self.ai1.name} vs {self.ai2.name}")
        print(f"Hands to play: {num_hands}")
        print(f"Starting chips: {self.starting_chips} each")
        print(f"Blinds: {self.small_blind}/{self.big_blind}")
        print("="*70)
        
        for hand_idx in range(num_hands):
            # Check if match should end (one AI out of chips)
            active_ais = [p for p in self.players if p.chips > 0]
            if len(active_ais) <= 1:
                print("\n" + "="*70)
                print("MATCH ENDED - One AI eliminated!")
                if active_ais:
                    print(f"Winner: {active_ais[0].name}")
                print("="*70)
                break
            
            # Play hand
            self.play_single_hand(verbose=verbose)
            
            # Reset for next hand
            self.game_state.reset_round()
            
            # Print progress every 5 hands if not verbose
            if not verbose and (hand_idx + 1) % 5 == 0:
                print(f"Progress: {hand_idx + 1}/{num_hands} hands completed")
        
        # Print final match statistics
        self._print_match_summary()
    
    def _print_match_summary(self):
        """Print final match statistics"""
        print("\n" + "="*70)
        print("MATCH SUMMARY")
        print("="*70)
        print(f"Total hands played: {self.hand_number}")
        print()
        print("Final chip counts:")
        print(f"  {self.ai1.name}: {self.ai1.chips} chips")
        print(f"  {self.ai2.name}: {self.ai2.chips} chips")
        print()
        print("Win statistics:")
        print(f"  {self.ai1.name} wins: {self.match_stats['ai1_wins']}")
        print(f"  {self.ai2.name} wins: {self.match_stats['ai2_wins']}")
        print()
        print("Profit/Loss:")
        print(f"  {self.ai1.name}: {self.match_stats['ai1_total_profit']:+d} chips")
        print(f"  {self.ai2.name}: {self.match_stats['ai2_total_profit']:+d} chips")
        print()
        
        # Determine overall winner
        if self.ai1.chips > self.ai2.chips:
            print(f"🏆 Overall Winner: {self.ai1.name}")
        elif self.ai2.chips > self.ai1.chips:
            print(f"🏆 Overall Winner: {self.ai2.name}")
        else:
            print("🤝 Match ended in a tie!")
        print("="*70)


# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    """
    Main demo function - runs AI vs AI poker match
    """
    print("\n" + "="*70)
    print(" "*20 + "AI vs AI POKER DEMO")
    print("="*70)
    print("\nThis demo showcases two Expectiminimax AI agents competing")
    print("in a Texas Hold'em poker match.")
    print()
    print("Configuration:")
    print("  - AI Agent 1: Search depth = 3 (deeper thinking)")
    print("  - AI Agent 2: Search depth = 2 (faster decisions)")
    print("  - Both use Monte Carlo hand strength evaluation")
    print("  - Both use the same strategic heuristics")
    print()
    
    # Get user input for match configuration
    print("Select match size:")
    print("  1. Quick demo (5 hands) - ~2 minutes")
    print("  2. Standard match (10 hands) - ~5 minutes")
    print("  3. Long match (20 hands) - ~10 minutes")
    
    choice = input("\nYour choice (1/2/3) [default: 2]: ").strip()
    
    hands_map = {"1": 5, "2": 10, "3": 20, "": 10}
    num_hands = hands_map.get(choice, 10)
    
    verbose_input = input("Show detailed action log? (y/n) [default: y]: ").strip().lower()
    verbose = verbose_input != 'n'
    
    print(f"\nStarting {num_hands}-hand match...")
    print("This may take a few minutes. Please wait...\n")
    
    # Create and run the demo
    demo = ai_vs_ai(
        starting_chips=1000,
        small_blind=10,
        big_blind=20
    )
    
    start_time = time.time()
    demo.play_match(num_hands=num_hands, verbose=verbose)
    end_time = time.time()
    
    print(f"\nTotal match time: {end_time - start_time:.1f} seconds")
    print("\n✓ Demo completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMatch interrupted by user.")
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()