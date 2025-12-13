"""
AI vs AI Poker Demo - COMPLETE FIXED VERSION
✅ Fixed chip accounting
✅ Restored intro text
✅ Fixed showdown crash when folded
"""

from game_manager import PokerGameManager
from expectiminimax import ExpectiminimaxAgent
from game_state import TexasHoldemGameState
import time


class ai_vs_ai:
    """Demo class for AI vs AI poker matches"""
    
    def __init__(self, starting_chips=1000, small_blind=10, big_blind=20):
        self.starting_chips = starting_chips
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        # Create two AI agents with different depths
        self.ai1 = ExpectiminimaxAgent(
            name="AI_Agent_1",
            chips=starting_chips,
            search_depth=2
        )
        
        self.ai2 = ExpectiminimaxAgent(
            name="AI_Agent_2", 
            chips=starting_chips,
            search_depth=2
        )
        
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
        """Play a single hand with corrected chip accounting"""
        self.hand_number += 1

        if verbose:
            print("\n" + "="*70)
            print(f"HAND #{self.hand_number}")
            print("="*70)

        # Track chips BEFORE any actions
        ai1_chips_before = self.ai1.chips
        ai2_chips_before = self.ai2.chips
        
        if verbose:
            print(f"\n💰 Starting Chips:")
            print(f"  AI_Agent_1: {ai1_chips_before} chips")
            print(f"  AI_Agent_2: {ai2_chips_before} chips")
            print(f"  Pot: {self.game_state.pot} (blinds posted)")

        # Track if hand went to showdown
        went_to_showdown = False

        # Play betting rounds
        for betting_round in ["preflop", "flop", "turn", "river"]:
            if verbose:
                print(f"\n--- {betting_round.upper()} ---")
                if betting_round != "preflop":
                    print(f"Community cards: {self.game_state.community_cards}")

            self._play_betting_round(verbose)

            # Check if hand ended early
            active_players = self.game_state.get_active_players()
            if len(active_players) <= 1:
                if verbose and active_players:
                    print(f"\n🏳️ {active_players[0].name} wins - opponent folded!")
                went_to_showdown = False
                break

            if betting_round == "river":
                went_to_showdown = True
                
            if betting_round != "river":
                self.game_state.advance_stage()

        # Capture pot before showdown
        pot_before_showdown = self.game_state.pot
        
        if verbose:
            print(f"\n💰 Pot before showdown: {pot_before_showdown}")

        # Determine winner
        winners = self.game_state.determine_winner()

        # ✅ FIX: Only print showdown if cards were dealt to river
        if verbose:
            if went_to_showdown and len(self.game_state.community_cards) == 5:
                print("\n--- SHOWDOWN ---")
                self._print_showdown()
            
            print("\n--- RESULTS ---")
            for winner, amount in winners:
                print(f"🏆 {winner.name} wins {amount} chips!")

        # Calculate profit
        ai1_chips_after = self.ai1.chips
        ai2_chips_after = self.ai2.chips
        
        ai1_profit = ai1_chips_after - ai1_chips_before
        ai2_profit = ai2_chips_after - ai2_chips_before

        if verbose:
            print(f"\n💰 Final Chips:")
            print(f"  AI_Agent_1: {ai1_chips_after} chips (profit: {ai1_profit:+d})")
            print(f"  AI_Agent_2: {ai2_chips_after} chips (profit: {ai2_profit:+d})")
            print(f"  Total: {ai1_chips_after + ai2_chips_after} chips")

        # Verify chip conservation
        total_chips = ai1_chips_after + ai2_chips_after
        expected_total = self.starting_chips * 2
        if total_chips != expected_total:
            print(f"\n⚠️ CHIP CONSERVATION ERROR!")
            print(f"  Expected: {expected_total}")
            print(f"  Actual: {total_chips}")
            print(f"  Difference: {expected_total - total_chips}")

        # Update statistics
        self.match_stats['ai1_total_profit'] += ai1_profit
        self.match_stats['ai2_total_profit'] += ai2_profit

        if ai1_profit > 0:
            self.match_stats['ai1_wins'] += 1
        elif ai2_profit > 0:
            self.match_stats['ai2_wins'] += 1
    
    def _play_betting_round(self, verbose=True):
        """Play through one betting round"""
        
        safety_counter = 0
        max_actions = 50
        
        while not self.game_state.is_betting_round_complete():
            safety_counter += 1
            
            if safety_counter > max_actions:
                if verbose:
                    print(f"\n⚠️ SAFETY STOP: Too many actions!")
                break
            
            active_with_chips = [
                p for p in self.game_state.get_active_players() 
                if p.chips > 0
            ]
            if len(active_with_chips) <= 1:
                break
            
            current_player = self.game_state.get_current_player()
            
            if current_player.chips == 0:
                if verbose:
                    print(f"  {current_player.name} is all-in, skipping")
                self.game_state.next_player()
                continue
            
            if verbose:
                self._print_player_turn(current_player)
            
            # Get AI decision
            start_time = time.time()
            action, amount = current_player.make_decision(self.game_state)
            decision_time = time.time() - start_time
            
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
            
            self.game_state.next_player()
            
            if all(p.folded or p.chips == 0 for p in self.game_state.players[:-1]):
                break
    
    def _print_player_turn(self, player):
        """Print player's current situation"""
        to_call = self.game_state.current_bet - player.current_bet
        
        print(f"\n🤖 {player.name}'s turn:")
        print(f"  Hole cards: {player.cards}")
        print(f"  Chips: {player.chips}")
        print(f"  Current bet: {player.current_bet}")
        print(f"  To call: {to_call}")
        print(f"  Pot: {self.game_state.pot}")
    
    def _print_showdown(self):
        """
        ✅ FIX: Only print if we have 5 community cards
        """
        if len(self.game_state.community_cards) < 5:
            print("Community cards: (incomplete board)")
            return
        
        print(f"Community cards: {self.game_state.community_cards}")
        print("\nFinal hands:")
        
        for player in self.game_state.get_active_players():
            full_hand = player.cards + self.game_state.community_cards
            
            # Safety check
            if len(full_hand) < 5:
                print(f"  {player.name}: {player.cards} (insufficient cards)")
                continue
            
            try:
                hand_eval = self.game_state.evaluator.evaluate_hand(full_hand)
                print(f"  {player.name}: {player.cards}")
                print(f"    → Rank: {hand_eval[0]}, Tiebreakers: {hand_eval[1]}")
            except Exception as e:
                print(f"  {player.name}: {player.cards} (evaluation error: {e})")
    
    def play_match(self, num_hands=10, verbose=True):
        """Play multiple hands as a match"""
        print("\n" + "="*70)
        print("AI vs AI POKER MATCH")
        print("="*70)
        print(f"Match: {self.ai1.name} vs {self.ai2.name}")
        print(f"Hands to play: {num_hands}")
        print(f"Starting chips: {self.starting_chips} each")
        print(f"Blinds: {self.small_blind}/{self.big_blind}")
        print("="*70)
        
        for hand_idx in range(num_hands):
            # Check if match should end
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
            
            # ✅ FIX: Only reset if match continues
            if hand_idx < num_hands - 1 and len([p for p in self.players if p.chips > 0]) > 1:
                self.game_state.reset_round()
            
            if not verbose and (hand_idx + 1) % 5 == 0:
                print(f"Progress: {hand_idx + 1}/{num_hands} hands completed")
        
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
    """Main demo function - runs AI vs AI poker match"""
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
    
    # Get user input
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
    
    # Create and run demo
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