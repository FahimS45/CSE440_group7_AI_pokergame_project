"""
Game Manager for Texas Hold'em Poker.
Direct integration without converter utility.
"""

from game_state import TexasHoldemGameState
from test_playerlogic import Player
from typing import List

class PokerGameManager:
    """
    Manages a Texas Hold'em poker game session.
    """
    
    def __init__(self, player_names: List[str], starting_chips: int = 1000, 
                 small_blind: int = 10, big_blind: int = 20):
        """
        Initialize poker game.
        
        Args:
            player_names: List of player names
            starting_chips: Starting chip count for each player
            small_blind: Small blind amount
            big_blind: Big blind amount
        """
        # Create players
        self.players = [Player(name, starting_chips) for name in player_names]
        
        # Create game state
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
        """Play through one betting round"""
        
        while not self.game_state.is_betting_round_complete():
            current_player = self.game_state.get_current_player()
            
            if verbose:
                self._print_player_turn(current_player)
            
            # Get player's decision
            game_state_dict = self.game_state.get_game_state_dict()
            action = current_player.make_decision(game_state_dict)
            
            # For now, players can only fold/check/call (no raising in base Player class)
            
            if action == "fold":
                self.game_state.apply_action(current_player, "fold")
                if verbose:
                    print(f"{current_player.name} folds")
            
            elif action == "check":
                try:
                    self.game_state.apply_action(current_player, "check")
                    if verbose:
                        print(f"{current_player.name} checks")
                except ValueError:
                    # Can't check, must call or fold
                    action = "call"
                    to_call = self.game_state.current_bet - current_player.current_bet
                    self.game_state.apply_action(current_player, "call")
                    if verbose:
                        print(f"{current_player.name} calls {to_call}")
            
            elif action == "call":
                to_call = self.game_state.current_bet - current_player.current_bet
                self.game_state.apply_action(current_player, "call")
                if verbose:
                    print(f"{current_player.name} calls {to_call}")
            
            # Move to next player
            self.game_state.next_player()
            
            # Safety check to prevent infinite loops
            if all(p.folded or p.chips == 0 for p in self.game_state.players[:-1]):
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
        # player.cards is already List[str] - no conversion needed!
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
            # player.cards is already List[str]
            full_hand = player.cards + self.game_state.community_cards
            
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


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("TEXAS HOLD'EM POKER SIMULATOR")
    print("="*60)
    
    # Create game with 4 players
    player_names = ["Alice", "Bob", "Charlie", "Diana"]
    game = PokerGameManager(
        player_names, 
        starting_chips=1000, 
        small_blind=10, 
        big_blind=20
    )
    
    # Play a single hand
    print("\n[Playing single hand for testing]")
    game.play_hand(verbose=True)
    
    # Reset and play tournament
    print("\n\n[Starting tournament]")
    game = PokerGameManager(
        player_names, 
        starting_chips=1000, 
        small_blind=10, 
        big_blind=20
    )
    game.play_tournament(num_hands=5, verbose=True)