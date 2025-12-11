"""
Main execution script for Expectiminimax AI Poker Experiments.
Runs AI against different opponent types and displays results.
"""

from experiments import ExperimentalSuite
import time


def generate_results_table(experiments):
    """Generate ASCII table from experiment metrics"""
    lines = []
    lines.append("="*84)
    lines.append("EXPERIMENTAL RESULTS - AI PERFORMANCE EVALUATION")
    lines.append("="*84)
    lines.append("")
    
    # Header
    header = f"{'Opponent':<24} {'Win Rate':>10} {'Profit':>12} {'ROI':>10} {'Hands':>8} {'Time/Dec':>10}"
    lines.append(header)
    lines.append("-"*84)
    
    # Data rows
    for exp in experiments:
        opp = exp.opponent_name
        win_rate = f"{exp.calculate_win_rate():.1f}%"
        profit = exp.calculate_profit()
        roi = f"{exp.calculate_roi():.1f}%"
        hands = exp.hands_played
        time_val = f"{exp.get_avg_decision_time():.3f}s"
        
        row = f"{opp:<24} {win_rate:>10} {profit:>12} {roi:>10} {hands:>8} {time_val:>10}"
        lines.append(row)
    
    lines.append("="*84)
    
    # Add analysis
    lines.append("")
    lines.append("ANALYSIS:")
    lines.append("-"*84)
    
    # Calculate aggregates
    total_hands = sum(exp.hands_played for exp in experiments)
    total_wins = sum(exp.hands_won_by_ai for exp in experiments)
    avg_win_rate = (total_wins / total_hands * 100) if total_hands > 0 else 0
    
    lines.append(f"Total hands played: {total_hands}")
    lines.append(f"Overall win rate: {avg_win_rate:.1f}%")
    
    # Best/worst matchups
    best = max(experiments, key=lambda e: e.calculate_win_rate())
    worst = min(experiments, key=lambda e: e.calculate_win_rate())
    
    lines.append(f"Best matchup: {best.opponent_name} ({best.calculate_win_rate():.1f}% win rate)")
    lines.append(f"Worst matchup: {worst.opponent_name} ({worst.calculate_win_rate():.1f}% win rate)")
    
    # Most profitable
    most_profitable = max(experiments, key=lambda e: e.calculate_profit())
    lines.append(f"Most profitable: {most_profitable.opponent_name} ({most_profitable.calculate_profit():+d} chips)")
    
    lines.append("="*84)
    
    return "\n".join(lines)


def main():
    """
    Main function - runs experiments and displays results summary.
    """
    print("\n" + "="*70)
    print(" "*10 + "EXPECTIMINIMAX AI - POKER EVALUATION")
    print("="*70)
    print("\nThis script will:")
    print("  • Run AI against 5 different opponent types")
    print("  • Collect performance metrics")
    print("  • Display results summary")
    print()
    
    # Configuration
    print("Configuration Options:")
    print("  1. Quick test (10 hands per opponent) - ~2-3 minutes")
    print("  2. Standard test (50 hands per opponent) - ~10-15 minutes")
    print("  3. Full test (100 hands per opponent) - ~20-30 minutes")
    print()
    
    choice = input("Select test size (1/2/3) [default: 2]: ").strip()
    if not choice:
        choice = "2"
    
    hands_map = {"1": 10, "2": 50, "3": 100}
    num_hands = hands_map.get(choice, 50)
    
    # Verbose option
    verbose_input = input("Show detailed hand-by-hand output? (y/n) [default: n]: ").strip().lower()
    verbose = (verbose_input == 'y')
    
    print(f"\n{'='*70}")
    print(f"Running {num_hands} hands per opponent...")
    if verbose:
        print("Verbose mode: ON (detailed output)")
    else:
        print("Verbose mode: OFF (summary only)")
    print(f"{'='*70}\n")
    
    # Run experiments
    start_time = time.time()
    
    suite = ExperimentalSuite()
    
    # Run experiments without saving
    print("="*70)
    print("RUNNING FULL EXPERIMENTAL SUITE")
    print("="*70)
    print(f"Experiments: {len(suite.opponent_types)}")
    print(f"Hands per experiment: {num_hands}")
    print(f"Total hands: {len(suite.opponent_types) * num_hands}")
    print()
    
    for i, (opponent_class, opponent_name) in enumerate(suite.opponent_types, 1):
        print(f"\n[{i}/{len(suite.opponent_types)}] Starting: {opponent_name}")
        
        metrics = suite.run_experiment(
            opponent_class=opponent_class,
            opponent_name=opponent_name,
            num_hands=num_hands,
            starting_chips=1000,
            verbose=verbose
        )
        
        suite.experiments.append(metrics)
        
        print(f"  ✓ Complete: {metrics.calculate_win_rate():.1f}% win rate, "
              f"{metrics.calculate_profit():+d} profit")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n{'='*70}")
    print(f"ALL EXPERIMENTS COMPLETE ({total_time:.1f}s)")
    print(f"{'='*70}\n")
    
    print(f"✓ Experiments completed in {total_time:.1f} seconds\n")
    
    # Display results table
    print(generate_results_table(suite.experiments))
    print()
    
    print("="*70)
    print("✓ SIMULATION COMPLETE!")
    print("="*70)
    print()


if __name__ == "__main__":
    try:
        main()
        print("🎉 Program completed successfully!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Experiment interrupted by user.\n")
        
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}\n")
        import traceback
        traceback.print_exc()
        print()
