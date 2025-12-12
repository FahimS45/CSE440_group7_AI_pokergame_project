"""
Experimental suite for evaluating Expectiminimax AI against different opponents.
UPDATED: Works with fixed $20 raise logic
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Type
from Deterministic_player_simulation.game_manager import PokerGameManager
from opponent_variants import (
    CallingStationPlayer,
    AggressivePlayer,
    TightPlayer,
    RandomPlayer,
    PassivePlayer
)
from Deterministic_player_simulation.abstracts import AbstractPlayer


class ExperimentMetrics:
    """Container for experiment metrics and statistics"""
    
    def __init__(self, opponent_name: str):
        self.opponent_name = opponent_name
        self.hands_played = 0
        self.hands_won_by_ai = 0
        self.hands_won_by_opponent = 0
        
        self.ai_starting_chips = 0
        self.ai_final_chips = 0
        self.opponent_starting_chips = 0
        self.opponent_final_chips = 0
        
        self.total_pot_won_by_ai = 0
        self.total_pot_lost_by_ai = 0
        self.largest_pot_won = 0
        self.largest_pot_lost = 0
        
        self.ai_actions = {'fold': 0, 'check': 0, 'call': 0, 'raise': 0}
        
        self.decision_times = []
        self.total_decisions = 0
        
        self.hands_to_showdown = 0
        self.hands_won_by_fold = 0
    
    def record_hand(self, ai_won: bool, pot_size: int, went_to_showdown: bool, won_by_fold: bool):
        """Record the outcome of a hand"""
        self.hands_played += 1
        
        if ai_won:
            self.hands_won_by_ai += 1
            self.total_pot_won_by_ai += pot_size
            self.largest_pot_won = max(self.largest_pot_won, pot_size)
        else:
            self.hands_won_by_opponent += 1
            self.total_pot_lost_by_ai += pot_size
            self.largest_pot_lost = max(self.largest_pot_lost, pot_size)
        
        if went_to_showdown:
            self.hands_to_showdown += 1
        
        if won_by_fold:
            self.hands_won_by_fold += 1
    
    def record_action(self, action: str):
        """Record an AI action"""
        if action in self.ai_actions:
            self.ai_actions[action] += 1
        self.total_decisions += 1
    
    def record_decision_time(self, time_seconds: float):
        """Record time taken for a decision"""
        self.decision_times.append(time_seconds)
    
    def calculate_win_rate(self) -> float:
        """Calculate AI win rate as percentage"""
        if self.hands_played == 0:
            return 0.0
        return (self.hands_won_by_ai / self.hands_played) * 100
    
    def calculate_profit(self) -> int:
        """Calculate net profit/loss for AI"""
        return self.ai_final_chips - self.ai_starting_chips
    
    def calculate_roi(self) -> float:
        """Calculate return on investment as percentage"""
        if self.ai_starting_chips == 0:
            return 0.0
        profit = self.calculate_profit()
        return (profit / self.ai_starting_chips) * 100
    
    def get_avg_decision_time(self) -> float:
        """Calculate average decision time"""
        if not self.decision_times:
            return 0.0
        return sum(self.decision_times) / len(self.decision_times)
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for JSON export"""
        return {
            'opponent_name': self.opponent_name,
            'hands_played': self.hands_played,
            'hands_won_by_ai': self.hands_won_by_ai,
            'hands_won_by_opponent': self.hands_won_by_opponent,
            'ai_win_rate': f"{self.calculate_win_rate():.1f}%",
            'profit': self.calculate_profit(),
            'roi': f"{self.calculate_roi():.1f}%",
            'ai_starting_chips': self.ai_starting_chips,
            'ai_final_chips': self.ai_final_chips,
            'largest_pot_won': self.largest_pot_won,
            'largest_pot_lost': self.largest_pot_lost,
            'hands_to_showdown': self.hands_to_showdown,
            'hands_won_by_fold': self.hands_won_by_fold,
            'ai_actions': self.ai_actions,
            'total_decisions': self.total_decisions,
            'avg_decision_time': f"{self.get_avg_decision_time():.3f}s",
            'decision_times': self.decision_times
        }


class ExperimentalSuite:
    """Main experimental framework for AI evaluation"""
    
    def __init__(self):
        self.experiments = []
        self.opponent_types = [
            (CallingStationPlayer, "Calling Station"),
            (AggressivePlayer, "Aggressive Player"),
            (TightPlayer, "Tight Player"),
            (RandomPlayer, "Random Player"),
            (PassivePlayer, "Passive Player")
        ]
    
    def run_experiment(
        self,
        opponent_class: Type[AbstractPlayer],
        opponent_name: str,
        num_hands: int = 50,
        starting_chips: int = 1000,
        verbose: bool = False
    ) -> ExperimentMetrics:
        """Run a single experiment against one opponent type"""
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"EXPERIMENT: AI vs {opponent_name}")
            print(f"{'='*70}")
            print(f"Hands to play: {num_hands}")
            print(f"Starting chips: {starting_chips}")
            print()
        
        metrics = ExperimentMetrics(opponent_name)
        metrics.ai_starting_chips = starting_chips
        metrics.opponent_starting_chips = starting_chips
        
        player_names = ["AI_Agent", opponent_name]
        game = PokerGameManager(
            player_names=player_names,
            ai_players=[0],
            starting_chips=starting_chips,
            small_blind=10,
            big_blind=20
        )
        
        hands_completed = 0
        
        for hand_num in range(1, num_hands + 1):
            if verbose and hand_num % 10 == 0:
                print(f"Progress: {hand_num}/{num_hands} hands...")
            
            active_players = [p for p in game.players if p.chips > 0]
            if len(active_players) <= 1:
                if verbose:
                    print(f"\nGame ended early: Only {len(active_players)} player(s) with chips")
                break
            
            try:
                self._play_hand_with_tracking(game, metrics, verbose)
                hands_completed += 1
            except Exception as e:
                print(f"❌ ERROR in hand {hand_num}: {e}")
                import traceback
                traceback.print_exc()
                break
            
            if hands_completed >= num_hands:
                break
        
        metrics.ai_final_chips = game.players[0].chips
        metrics.opponent_final_chips = game.players[1].chips
        
        if verbose:
            print(f"\n{'='*70}")
            print("EXPERIMENT COMPLETE")
            print(f"{'='*70}")
            print(f"Hands played: {metrics.hands_played}")
            print(f"AI win rate: {metrics.calculate_win_rate():.1f}%")
            print(f"AI profit: {metrics.calculate_profit():+d} chips")
            print()
        
        return metrics
    
    def _play_hand_with_tracking(self, game: PokerGameManager, metrics: ExperimentMetrics, verbose: bool):
        """Play a single hand while tracking metrics"""
        game.hand_number += 1
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"HAND #{game.hand_number}")
            print(f"{'='*60}")
        
        went_to_showdown = False
        won_by_fold = False
        
        for betting_round in ["preflop", "flop", "turn", "river"]:
            if verbose:
                print(f"\n--- {betting_round.upper()} ---")
                if betting_round != "preflop":
                    print(f"Community cards: {game.game_state.community_cards}")
            
            self._play_betting_round_with_tracking(game, metrics, verbose)
            
            active_players = game.game_state.get_active_players()
            if len(active_players) <= 1:
                won_by_fold = True
                if verbose:
                    print(f"\nAll players folded except {active_players[0].name}")
                break
            
            if betting_round != "river":
                game.game_state.advance_stage()
        
        pot_size = game.game_state.pot
        winners = game.game_state.determine_winner()
        
        ai_won = any(winner.name == "AI_Agent" for winner, _ in winners)
        
        active_players = game.game_state.get_active_players()
        went_to_showdown = len(active_players) > 1
        
        metrics.record_hand(ai_won, pot_size, went_to_showdown, won_by_fold)
        
        if verbose:
            print("\n--- RESULTS ---")
            for winner, amount in winners:
                print(f"{winner.name} wins {amount} chips!")
        
        game.game_state.reset_round()
    
    def _play_betting_round_with_tracking(self, game: PokerGameManager, metrics: ExperimentMetrics, verbose: bool):
        """Play betting round while tracking AI actions"""
        
        safety_counter = 0
        max_actions = 50
        
        while not game.game_state.is_betting_round_complete():
            safety_counter += 1
            
            if safety_counter > max_actions:
                if verbose:
                    print(f"\n⚠️ SAFETY STOP!")
                break
            
            active_with_chips = [p for p in game.game_state.get_active_players() if p.chips > 0]
            if len(active_with_chips) <= 1:
                break
            
            current_player = game.game_state.get_current_player()
            
            if current_player.chips == 0:
                game.game_state.next_player()
                continue
            
            if verbose:
                print(f"\n{current_player.name}'s turn:")
                print(f"  Chips: {current_player.chips}")
                print(f"  To call: {game.game_state.current_bet - current_player.current_bet}")
            
            # Get action
            if current_player.name == "AI_Agent":
                start_time = time.time()
                action_result = current_player.make_decision(game.game_state)
                decision_time = time.time() - start_time
                
                if isinstance(action_result, tuple):
                    action, amount = action_result
                else:
                    action = action_result
                    amount = 0
                
                metrics.record_action(action)
                metrics.record_decision_time(decision_time)
            else:
                game_state_dict = game.game_state.get_game_state_dict()
                action = current_player.make_decision(game_state_dict)
                amount = 0
            
            # Apply action
            if action == "fold":
                game.game_state.apply_action(current_player, "fold")
                if verbose:
                    print(f"{current_player.name} folds")
            
            elif action == "check":
                game.game_state.apply_action(current_player, "check")
                if verbose:
                    to_call = game.game_state.current_bet - current_player.current_bet
                    if to_call > 0:
                        print(f"{current_player.name} calls {to_call} (auto-call)")
                    else:
                        print(f"{current_player.name} checks")
            
            elif action == "call":
                to_call = game.game_state.current_bet - current_player.current_bet
                game.game_state.apply_action(current_player, "call")
                if verbose:
                    print(f"{current_player.name} calls {to_call}")
            
            elif action == "raise":
                if current_player.name == "AI_Agent":
                    game.game_state.apply_action(current_player, "raise", amount)
                    if verbose:
                        print(f"{current_player.name} raises to {amount}")
                else:
                    to_call = game.game_state.current_bet - current_player.current_bet
                    if to_call > 0:
                        game.game_state.apply_action(current_player, "call")
                        if verbose:
                            print(f"{current_player.name} calls {to_call}")
                    else:
                        game.game_state.apply_action(current_player, "check")
                        if verbose:
                            print(f"{current_player.name} checks")
            
            game.game_state.next_player()
            
            if all(p.folded or p.chips == 0 for p in game.game_state.players[:-1]):
                break
    
    def run_all_experiments(
        self,
        num_hands_per_experiment: int = 50,
        starting_chips: int = 1000,
        verbose: bool = False
    ):
        """Run experiments against all opponent types"""
        
        print("\n" + "="*70)
        print("RUNNING FULL EXPERIMENTAL SUITE")
        print("="*70)
        print(f"Experiments: {len(self.opponent_types)}")
        print(f"Hands per experiment: {num_hands_per_experiment}")
        print(f"Total hands: {len(self.opponent_types) * num_hands_per_experiment}")
        print()
        
        start_time = time.time()
        
        for i, (opponent_class, opponent_name) in enumerate(self.opponent_types, 1):
            print(f"\n[{i}/{len(self.opponent_types)}] Starting: {opponent_name}")
            
            metrics = self.run_experiment(
                opponent_class=opponent_class,
                opponent_name=opponent_name,
                num_hands=num_hands_per_experiment,
                starting_chips=starting_chips,
                verbose=verbose
            )
            
            self.experiments.append(metrics)
            
            print(f"  ✓ Complete: {metrics.calculate_win_rate():.1f}% win rate, "
                  f"{metrics.calculate_profit():+d} profit")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "="*70)
        print(f"ALL EXPERIMENTS COMPLETE ({total_time:.1f}s)")
        print("="*70)
        
        self.save_results()
    
    def save_results(self, filename: str = None):
        """Save experiment results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"experiment_results_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'num_experiments': len(self.experiments),
            'experiments': [exp.to_dict() for exp in self.experiments]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
        return filename