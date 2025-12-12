"""
Human vs AI Texas Hold'em Poker
Player makes decisions via terminal input
"""

from test_game_state import TexasHoldemGameState
from test_expectiminimax import ExpectiminimaxAgent
from test_abstracts import AbstractPlayer


class HumanPlayer(AbstractPlayer):
    """
    Human player that gets input from terminal
    """
    
    def __init__(self, name: str, chips: int):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
    
    def make_decision(self, game_state) -> tuple:
        """
        Get human player's decision from terminal input
        Returns: (action, amount) tuple like AI
        """
        # Show current situation
        print(f"\n{'='*60}")
        print(f"YOUR TURN - {self.name}")
        print(f"{'='*60}")
        print(f"Your hole cards: {self.cards}")
        print(f"Community cards: {game_state.get_community_cards()}")
        print(f"Your chips: {self.chips}")
        print(f"Your current bet this round: {self.current_bet}")
        print(f"Current pot: {game_state.get_pot_size()}")
        print(f"Current bet to match: {game_state.get_current_bet()}")
        
        # Calculate amount needed to call
        to_call = game_state.get_current_bet() - self.current_bet
        
        # Get legal actions
        legal_actions = game_state.get_legal_actions(self)
        
        # Display options
        print(f"\n{'='*60}")
        print("LEGAL ACTIONS:")
        print(f"{'='*60}")
        
        action_map = {}
        idx = 1
        
        for action, amount in legal_actions:
            if action == 'fold':
                print(f"  [{idx}] FOLD - Give up this hand")
                action_map[idx] = ('fold', 0)
                idx += 1
            elif action == 'check':
                print(f"  [{idx}] CHECK - No bet (free)")
                action_map[idx] = ('check', 0)
                idx += 1
            elif action == 'call':
                print(f"  [{idx}] CALL {to_call} chips - Match current bet")
                action_map[idx] = ('call', 0)
                idx += 1
            elif action == 'raise':
                print(f"  [{idx}] RAISE to {amount} chips (costs {amount - self.current_bet} more)")
                action_map[idx] = ('raise', amount)
                idx += 1
        
        # Get player choice
        while True:
            try:
                choice = input(f"\nEnter your choice (1-{len(action_map)}): ").strip()
                choice_num = int(choice)
                
                if choice_num in action_map:
                    selected_action = action_map[choice_num]
                    action_name = selected_action[0]
                    
                    # Confirm action
                    if action_name == 'fold':
                        confirm = input("Are you sure you want to fold? (yes/no): ").strip().lower()
                        if confirm != 'yes':
                            continue
                    elif action_name == 'raise':
                        print(f"Raising to {selected_action[1]} chips")
                    
                    return selected_action
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(action_map)}")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\n\nGame interrupted by player.")
                return ('fold', 0)
    
    def update_stack(self, amount: int):
        """Update chip count"""
        self.chips += amount
    
    def reset_hand(self):
        """Reset for new hand"""
        self.cards = []
        self.current_bet = 0
        self.folded = False


class HumanVsAIGame:
    """
    Manages a Human vs AI poker game
    """
    
    def __init__(self, human_name: str = "You", starting_chips: int = 1000,
                 small_blind: int = 10, big_blind: int = 20, ai_depth: int = 2):
        """
        Initialize game
        
        Args:
            human_name: Human player's name
            starting_chips: Starting chips for both players
            small_blind: Small blind amount
            big_blind: Big blind amount
            ai_depth: AI search depth (2=fast, 3=medium, 4+=slow)
        """
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
    
    def play_hand(self):
        """Play a single hand of poker"""
        self.hand_number += 1
        
        print("\n" + "="*60)
        print(f"HAND #{self.hand_number}")
        print("="*60)
        self._print_status()
        
        # Play through betting rounds
        for betting_round in ["preflop", "flop", "turn", "river"]:
            print(f"\n{'='*60}")
            print(f"{betting_round.upper()}")
            print(f"{'='*60}")
            
            if betting_round != "preflop":
                print(f"Community cards: {self.game_state.community_cards}")
                print(f"Pot: {self.game_state.pot}")
            
            self._play_betting_round()
            
            # Check if hand ended early
            active = self.game_state.get_active_players()
            if len(active) <= 1:
                winner = active[0]
                print(f"\n🏆 {winner.name} wins {self.game_state.pot} chips (opponent folded)!")
                break
            
            # Advance to next stage
            if betting_round != "river":
                self.game_state.advance_stage()
        else:
            # Showdown
            self._showdown()
        
        # Print results
        self._print_status()
        input("\nPress Enter to continue...")
    
    def _play_betting_round(self):
        """Play one betting round"""
        safety = 0
        max_actions = 50
        
        while not self.game_state.is_betting_round_complete():
            safety += 1
            if safety > max_actions:
                print("⚠️ Safety limit reached")
                break
            
            # Check active players
            active = [p for p in self.game_state.get_active_players() if p.chips > 0]
            if len(active) <= 1:
                break
            
            current = self.game_state.get_current_player()
            
            # Skip if all-in
            if current.chips == 0:
                print(f"\n{current.name} is all-in")
                self.game_state.next_player()
                continue
            
            # Get decision
            if isinstance(current, HumanPlayer):
                action, amount = current.make_decision(self.game_state)
            else:
                # AI decision
                print(f"\n🤖 AI is thinking...")
                action, amount = current.make_decision(self.game_state)
                
                # Show AI action
                if action == 'fold':
                    print(f"AI folds")
                elif action == 'check':
                    to_call = self.game_state.current_bet - current.current_bet
                    if to_call > 0:
                        print(f"AI calls {to_call} chips")
                    else:
                        print(f"AI checks")
                elif action == 'call':
                    to_call = self.game_state.current_bet - current.current_bet
                    print(f"AI calls {to_call} chips")
                elif action == 'raise':
                    print(f"AI raises to {amount} chips!")
            
            # Apply action
            self.game_state.apply_action(current, action, amount)
            
            # Next player
            self.game_state.next_player()
            
            # Check if only one player left
            if all(p.folded or p.chips == 0 for p in self.game_state.players[:-1]):
                break
    
    def _showdown(self):
        """Show final hands and determine winner"""
        print(f"\n{'='*60}")
        print("SHOWDOWN")
        print(f"{'='*60}")
        print(f"Community cards: {self.game_state.community_cards}")
        print()
        
        # Show hands
        for player in self.game_state.get_active_players():
            full_hand = player.cards + self.game_state.community_cards
            hand_eval = self.game_state.evaluator.evaluate_hand(full_hand)
            print(f"{player.name}: {player.cards}")
            print(f"  Rank: {hand_eval[0]}, Kickers: {hand_eval[1]}")
        
        # Determine winner
        winners = self.game_state.determine_winner()
        print()
        for winner, amount in winners:
            print(f"🏆 {winner.name} wins {amount} chips!")
    
    def _print_status(self):
        """Print current chip counts"""
        print(f"\n{'='*60}")
        print("CHIP COUNTS")
        print(f"{'='*60}")
        for player in self.players:
            print(f"  {player.name}: {player.chips} chips")
        print(f"  Pot: {self.game_state.pot}")
        print(f"{'='*60}")
    
    def play_game(self):
        """Main game loop"""
        print("\n" + "="*60)
        print("TEXAS HOLD'EM - HUMAN VS AI")
        print("="*60)
        print(f"Starting chips: {self.starting_chips}")
        print(f"Blinds: {self.game_state.small_blind}/{self.game_state.big_blind}")
        print("="*60)
        
        while True:
            # Check if game should end
            active = [p for p in self.players if p.chips > 0]
            if len(active) <= 1:
                print("\n" + "="*60)
                print("GAME OVER")
                print("="*60)
                if active:
                    print(f"Winner: {active[0].name}")
                break
            
            # Play hand
            self.play_hand()
            
            # Ask to continue
            cont = input("\nPlay another hand? (yes/no): ").strip().lower()
            if cont != 'yes':
                print("\nThanks for playing!")
                self._print_status()
                break
            
            # Reset for next hand
            self.game_state.reset_round()


# Run the game
if __name__ == "__main__":
    try:
        print("\nWelcome to Texas Hold'em Poker!")
        print("\nYou'll play against an AI using the Expectiminimax algorithm.")
        
        # Get player name
        name = input("\nEnter your name: ").strip() or "Player"
        
        # Get difficulty
        print("\nSelect AI difficulty:")
        print("  1. Easy (depth=1, very fast)")
        print("  2. Medium (depth=2, fast)")
        print("  3. Hard (depth=3, slower)")
        
        difficulty = input("Your choice (1-3): ").strip()
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
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()