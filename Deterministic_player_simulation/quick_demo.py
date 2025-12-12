"""
Quick demonstration script to run experiments and generate report.
Perfect for testing and generating results for project presentation.
"""

from experimental_suite import ExperimentalSuite
from report_generator import ReportGenerator
import time


def main():
    """
    Main demo function - runs experiments and generates reports.
    """
    print("\n" + "="*70)
    print(" "*15 + "EXPECTIMINIMAX AI - POKER SIMULATION")
    print("="*70)
    print("\nThis script will:")
    print("  1. Run AI against 5 different opponent types")
    print("  2. Collect performance metrics")
    print("  3. Generate comprehensive reports")
    print("  4. Create visualization-ready data")
    print()
    
    # Get user input
    print("Select experiment size:")
    print("  1. Quick test (10 hands per opponent) - ~2 minutes")
    print("  2. Standard test (50 hands per opponent) - ~10 minutes")
    print("  3. Full test (100 hands per opponent) - ~20 minutes")
    
    choice = input("\nYour choice (1/2/3): ").strip()
    
    hands_map = {"1": 10, "2": 50, "3": 100}
    num_hands = hands_map.get(choice, 50)
    
    print(f"\nRunning {num_hands} hands per opponent...")
    print("This may take a few minutes. Please wait...\n")
    
    # Run experiments
    start_time = time.time()
    
    suite = ExperimentalSuite()
    suite.run_all_experiments(
        num_hands_per_experiment=num_hands,
        starting_chips=1000,
        verbose=True
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n✓ Experiments completed in {total_time:.1f} seconds")
    print()
    
    # Find the most recent results file
    import glob
    files = glob.glob("experiment_results_*.json")
    if not files:
        print("Error: No results file found!")
        return
    
    latest_file = max(files)
    print(f"Results saved to: {latest_file}")
    print()
    
    # Generate reports
    print("Generating reports...")
    generator = ReportGenerator(latest_file)
    
    # Console summary
    print("\n" + generator.generate_ascii_table())
    
    # Generate all report formats
    print("\nGenerating additional report formats...")
    generator.generate_full_report("experiment_report.txt")
    generator.generate_csv("experiment_results.csv")
    
    with open("results_markdown.md", 'w') as f:
        f.write(generator.generate_markdown_table())
    
    with open("results_latex.tex", 'w') as f:
        f.write(generator.generate_latex_table())
    
    print("\n" + "="*70)
    print("✓ ALL REPORTS GENERATED SUCCESSFULLY!")
    print("="*70)
    print("\nGenerated files:")
    print(f"  • {latest_file} (Raw data - JSON)")
    print("  • experiment_report.txt (Full analysis)")
    print("  • experiment_results.csv (Spreadsheet data)")
    print("  • results_markdown.md (For README)")
    print("  • results_latex.tex (For academic paper)")
    print()
    print("You can now:")
    print("  1. Open experiment_report.txt for full analysis")
    print("  2. Import experiment_results.csv into Excel for graphs")
    print("  3. Copy tables from markdown/latex files for your report")
    print()
    print("="*70)


def print_usage_guide():
    """Print guide on how to use the results"""
    print("\n" + "="*70)
    print("HOW TO USE THESE RESULTS IN YOUR PROJECT REPORT")
    print("="*70)
    print()
    
    print("SECTION 1: Experimental Setup")
    print("-"*70)
    print("Copy this configuration:")
    print("  • Algorithm: Expectiminimax with Monte Carlo evaluation")
    print("  • Search depth: 2 levels")
    print("  • Monte Carlo simulations: 500 per leaf node")
    print("  • Chance node sampling: 8 cards")
    print("  • Action abstraction: 4-7 actions per state")
    print("  • Starting chips: 1000 per player")
    print("  • Blinds: 10/20")
    print()
    
    print("SECTION 2: Opponent Types")
    print("-"*70)
    print("Describe each opponent:")
    print("  • Calling Station: Always calls, never folds")
    print("  • Aggressive Player: Always bets/raises aggressively")
    print("  • Tight Player: Folds frequently, plays conservatively")
    print("  • Random Player: Makes random decisions (baseline)")
    print("  • Passive Player: Never raises, defensive play")
    print()
    
    print("SECTION 3: Results")
    print("-"*70)
    print("Use the generated tables (results_markdown.md or results_latex.tex)")
    print("Include these metrics:")
    print("  • Win rate (percentage)")
    print("  • Profit/loss (chips)")
    print("  • ROI (return on investment)")
    print("  • Average decision time")
    print()
    
    print("SECTION 4: Analysis")
    print("-"*70)
    print("Key points to discuss:")
    print("  • AI performs best against predictable opponents")
    print("  • Struggles slightly against tight/defensive play")
    print("  • Average decision time shows computational efficiency")
    print("  • Positive ROI demonstrates consistent value extraction")
    print()
    
    print("SECTION 5: Visualizations")
    print("-"*70)
    print("Create these graphs in Excel using experiment_results.csv:")
    print("  • Bar chart: Win rate vs opponent type")
    print("  • Bar chart: Profit vs opponent type")
    print("  • Line graph: Cumulative profit over hands")
    print("  • Pie chart: Distribution of AI actions")
    print()
    
    print("="*70)
    print()


if __name__ == "__main__":
    try:
        main()
        
        # Ask if user wants usage guide
        show_guide = input("\nShow usage guide for project report? (y/n): ").strip().lower()
        if show_guide == 'y':
            print_usage_guide()
        
        print("Demo completed successfully! 🎉")
        print()
        
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user.")
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()