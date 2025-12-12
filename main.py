"""
Human vs AI Texas Hold'em Poker
✅ NEW: Hidden actions - players don't see each other's decisions until showdown
✅ Shows: Flop, Turn, River, Current Bet, Pot
"""

from Deterministic_player_simulation.game_state import TexasHoldemGameState
from Deterministic_player_simulation.expectiminimax import ExpectiminimaxAgent
from Deterministic_player_simulation.abstracts import AbstractPlayer


class HumanPlayer(AbstractPlayer):
    """
    Human player with terminal input
    """
    
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
    
    def make_decision(self, game_state) -> tuple:
        """
        Get human decision from terminal
        ✅ Only shows PUBLIC information (community cards, pot, current bet)
        """
        print(f"\n{'='*70}")
        print(f"YOUR TURN - {self.name}")
        print(f"{'='*70}")
        print(f"🃏 Your hole cards: {self.cards}")
        print(f"🌍 Community cards: {game_state.get_community_cards()}")
        print(f"💰 Pot: {game_state.get_pot_size()}")
        print(f"📊 Current bet to match: {game_state.get_current_bet()}")
        print(f"💵 Your chips: {self.chips}")
        print(f"🎯 Your current bet this round: {self.current_bet}")
        
        to_call = game_state.get_current_bet() - self.current_bet
        
        # Get legal actions
        legal_actions = game_state.get_legal_actions(self)
        
        print(f"\n{'='*70}")
        print("⚡ AVAILABLE ACTIONS:")
        print(f"{'='*70}")
        
        action_map = {}
        idx = 1
        
        for action, amount in legal_actions:
            if action == 'fold':
                print(f"  [{idx}] ❌ FOLD - Give up this hand")
                action_map[idx] = ('fold', 0)
                idx += 1
            elif action == 'check':
                print(f"  [{idx}] ✅ CHECK - No bet (free)")
                action_map[idx] = ('check', 0)
                idx += 1
            elif action == 'call':
                print(f"  [{idx}] 📞 CALL {to_call} chips - Match current bet")
                action_map[idx] = ('call', 0)
                idx += 1
            elif action == 'raise':
                cost = amount - self.current_bet
                print(f"  [{idx}] 🚀 RAISE to {amount} chips (costs {cost} more)")
                action_map[idx] = ('raise', amount)
                idx += 1
        
        # Get choice
        while True:
            try:
                choice = input(f"\n👉 Enter your choice (1-{len(action_map)}): ").strip()
                choice_num = int(choice)
                
                if choice_num in action_map:
                    selected_action = action_map[choice_num]
                    action_name = selected_action[0]
                    
                    # Confirm fold
                    if action_name == 'fold':
                        confirm = input("⚠️  Are you sure you want to FOLD? (yes/no): ").strip().lower()
                        if confirm != 'yes':
                            continue
                    
                    return selected_action
                else:
                    print(f"❌ Invalid. Enter 1-{len(action_map)}")
            except ValueError:
                print("❌ Please enter a number")
            except KeyboardInterrupt:
                print("\n\n⚠️  Game interrupted")
                return ('fold', 0)
    
    def update_stack(self, amount: int):
        self.chips += amount
    
    def reset_hand(self):
        self.cards = []
        self.current_bet = 0
        self.folded = False


class HumanVsAIGame:
    """
    Poker game with HIDDEN actions
    """
    
    def __init__(self, human_name: str = "You", starting_chips: int = 1000,
                 small_blind: int = 10, big_blind: int = 20, ai_depth: int = 2):
        self.human = HumanPlayer(human_name, starting_chips)
        self.ai = ExpectiminimaxAgent("AI_Agent", starting_chips, search_depth=ai_depth)
        
        self.players = [self.human, self.ai]
        self.game_state = TexasHoldemGameState(
            self.players,
            small_blind=small_blind,
            big_blind=big_blind
        )
        
        self.hand_number = 0
        self.starting_chips = starting_chips
        
        # Track actions for showdown reveal
        self.action_history = []
    
    def play_hand(self):
        """Play one hand with HIDDEN actions"""
        self.hand_number += 1
        self.action_history = []
        
        print("\n" + "="*70)
        print(f"🎲 HAND #{self.hand_number}")
        print("="*70)
        self._print_status()
        
        # Play through betting rounds
        for betting_round in ["preflop", "flop", "turn", "river"]:
            print(f"\n{'='*70}")
            print(f"🎴 {betting_round.upper()}")
            print(f"{'='*70}")
            
            # Show community cards (except preflop)
            if betting_round != "preflop":
                print(f"🌍 Community cards: {self.game_state.community_cards}")
                print(f"💰 Pot: {self.game_state.pot}")
            
            self._play_betting_round(betting_round)
            
            # Check if hand ended
            active = self.game_state.get_active_players()
            if len(active) <= 1:
                winner = active[0]
                print(f"\n{'='*70}")
                print(f"🏆 {winner.name} wins {self.game_state.pot} chips!")
                print(f"{'='*70}")
                print(f"💡 Reason: Opponent folded")
                self._reveal_action_history()
                break
            
            # Advance stage
            if betting_round != "river":
                self.game_state.advance_stage()
        else:
            # Showdown
            self._showdown()
        
        self._print_status()
        input("\n⏸️  Press Enter to continue...")
    
    def _play_betting_round(self, round_name: str):
        """
        Play betting round with HIDDEN actions
        ✅ Actions are logged but not displayed immediately
        """
        safety = 0
        max_actions = 50
        
        while not self.game_state.is_betting_round_complete():
            safety += 1
            if safety > max_actions:
                print("⚠️  Safety limit")
                break
            
            active = [p for p in self.game_state.get_active_players() if p.chips > 0]
            if len(active) <= 1:
                break
            
            current = self.game_state.get_current_player()
            
            if current.chips == 0:
                self.game_state.next_player()
                continue
            
            # Get decision (HIDDEN from opponent)
            if isinstance(current, HumanPlayer):
                action, amount = current.make_decision(self.game_state)
                
                # ✅ Don't show details - just confirm action taken
                print(f"\n✅ Your action recorded")
                
            else:
                # AI decision (HIDDEN from human)
                print(f"\n🤖 AI is thinking...")
                action, amount = current.make_decision(self.game_state)
                print(f"✅ AI action recorded")
            
            # Record action for later reveal
            to_call = self.game_state.current_bet - current.current_bet
            self.action_history.append({
                'round': round_name,
                'player': current.name,
                'action': action,
                'amount': amount,
                'to_call': to_call
            })
            
            # Apply action
            self.game_state.apply_action(current, action, amount)
            self.game_state.next_player()
            
            if all(p.folded or p.chips == 0 for p in self.game_state.players[:-1]):
                break
    
    def _showdown(self):
        """Show final hands and determine winner"""
        print(f"\n{'='*70}")
        print("🎯 SHOWDOWN")
        print(f"{'='*70}")
        print(f"🌍 Final community cards: {self.game_state.community_cards}")
        print()
        
        # Show both hands
        for player in self.game_state.get_active_players():
            full_hand = player.cards + self.game_state.community_cards
            hand_eval = self.game_state.evaluator.evaluate_hand(full_hand)
            hand_rank_names = {
                10: "Royal Flush", 9: "Straight Flush", 8: "Four of a Kind",
                7: "Full House", 6: "Flush", 5: "Straight",
                4: "Three of a Kind", 3: "Two Pair", 2: "One Pair", 1: "High Card"
            }
            print(f"🃏 {player.name}: {player.cards}")
            print(f"   → {hand_rank_names.get(hand_eval[0], 'Unknown')}")
        
        # Winner
        winners = self.game_state.determine_winner()
        print()
        for winner, amount in winners:
            print(f"{'='*70}")
            print(f"🏆 {winner.name} WINS {amount} chips!")
            print(f"{'='*70}")
        
        # Reveal action history
        self._reveal_action_history()
    
    def _reveal_action_history(self):
        """
        ✅ NEW: Reveal all actions taken during the hand
        """
        print(f"\n{'='*70}")
        print("📜 ACTION HISTORY (Now Revealed)")
        print(f"{'='*70}")
        
        current_round = None
        for action in self.action_history:
            if action['round'] != current_round:
                current_round = action['round']
                print(f"\n--- {current_round.upper()} ---")
            
            player = action['player']
            act = action['action']
            amt = action['amount']
            to_call = action['to_call']
            
            if act == 'fold':
                print(f"  ❌ {player} folded")
            elif act == 'check':
                if to_call > 0:
                    print(f"  📞 {player} called {to_call}")
                else:
                    print(f"  ✅ {player} checked")
            elif act == 'call':
                print(f"  📞 {player} called {to_call}")
            elif act == 'raise':
                print(f"  🚀 {player} raised to {amt}")
        
        print(f"{'='*70}")
    
    def _print_status(self):
        """Print chip counts"""
        print(f"\n{'='*70}")
        print("💰 CHIP COUNTS")
        print(f"{'='*70}")
        for player in self.players:
            print(f"  {player.name}: {player.chips} chips")
        print(f"  Pot: {self.game_state.pot}")
        print(f"{'='*70}")
    
    def play_game(self):
        """Main game loop"""
        print("\n" + "="*70)
        print("♠️♥️ TEXAS HOLD'EM - HUMAN VS AI ♣️♦️")
        print("="*70)
        print(f"Starting chips: {self.starting_chips}")
        print(f"Blinds: {self.game_state.small_blind}/{self.game_state.big_blind}")
        print("\n⚠️  IMPORTANT: Actions are HIDDEN until showdown!")
        print("="*70)
        
        while True:
            # Check if game should end
            active = [p for p in self.players if p.chips > 0]
            if len(active) <= 1:
                print("\n" + "="*70)
                print("🎮 GAME OVER")
                print("="*70)
                if active:
                    print(f"🏆 Winner: {active[0].name}")
                self._print_status()
                break
            
            # Play hand
            self.play_hand()
            
            # Ask to continue
            cont = input("\n🎲 Play another hand? (yes/no): ").strip().lower()
            if cont != 'yes':
                print("\n👋 Thanks for playing!")
                self._print_status()
                break
            
            # Reset for next hand
            self.game_state.reset_round()


if __name__ == "__main__":
    try:
        print("\n🎰 Welcome to Texas Hold'em Poker!")
        print("="*70)
        
        # Get player name
        name = input("Enter your name: ").strip() or "Player"
        
        # Get difficulty
        print("\n🎯 Select AI difficulty:")
        print("  1. Easy (depth=1, very fast)")
        print("  2. Medium (depth=2, fast)")
        print("  3. Hard (depth=3, slower)")
        
        difficulty = input("\nYour choice (1-3): ").strip()
        depth_map = {'1': 1, '2': 2, '3': 3}
        ai_depth = depth_map.get(difficulty, 2)
        
        # Start game
        game = HumanVsAIGame(
            human_name=name,
            starting_chips=1000,
            small_blind=10,
            big_blind=20,
            ai_depth=ai_depth
        )
        
        game.play_game()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Game interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()