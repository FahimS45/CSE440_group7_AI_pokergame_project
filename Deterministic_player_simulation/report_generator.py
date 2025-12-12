"""
Generate formatted tables and visualizations for project report.
Creates publication-ready tables and plots from experimental results.
"""

import json
from typing import List, Dict
from datetime import datetime


class ReportGenerator:
    """Generate formatted output for project report"""
    
    def __init__(self, results_file: str = None):
        """
        Load results from JSON file.
        
        Args:
            results_file: Path to experiment results JSON
        """
        self.results = []
        if results_file:
            self.load_results(results_file)
    
    def load_results(self, filename: str):
        """Load experiment results from JSON"""
        with open(filename, 'r') as f:
            data = json.load(f)
            self.results = data['experiments']
            self.timestamp = data.get('timestamp', 'Unknown')
    
    def generate_latex_table(self) -> str:
        """
        Generate LaTeX table for academic report.
        
        Returns:
            LaTeX table code as string
        """
        latex = []
        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{AI Performance Against Different Opponent Strategies}")
        latex.append("\\label{tab:ai_performance}")
        latex.append("\\begin{tabular}{|l|c|c|c|c|c|}")
        latex.append("\\hline")
        latex.append("\\textbf{Opponent} & \\textbf{Win Rate} & \\textbf{Profit} & "
                    "\\textbf{ROI} & \\textbf{Hands} & \\textbf{Avg Time} \\\\")
        latex.append("\\hline")
        
        for result in self.results:
            opp = result['opponent_name']
            win_rate = result['ai_win_rate']
            profit = result['profit']
            roi = result['roi']
            hands = result['hands_played']
            time = result['avg_decision_time']
            
            latex.append(f"{opp} & {win_rate} & {profit:+d} & {roi} & {hands} & {time} \\\\")
        
        latex.append("\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")
        
        return "\n".join(latex)
    
    def generate_markdown_table(self) -> str:
        """
        Generate Markdown table for README or documentation.
        
        Returns:
            Markdown table as string
        """
        md = []
        md.append("## Experimental Results\n")
        md.append("| Opponent Strategy | Win Rate | Profit | ROI | Hands Played | Avg Decision Time |")
        md.append("|------------------|----------|--------|-----|--------------|-------------------|")
        
        for result in self.results:
            opp = result['opponent_name']
            win_rate = result['ai_win_rate']
            profit = result['profit']
            roi = result['roi']
            hands = result['hands_played']
            time = result['avg_decision_time']
            
            md.append(f"| {opp} | {win_rate} | {profit:+d} | {roi} | {hands} | {time} |")
        
        return "\n".join(md)
    
    def generate_ascii_table(self) -> str:
        """
        Generate ASCII table for terminal/report.
        
        Returns:
            ASCII table as string
        """
        lines = []
        lines.append("="*80)
        lines.append("EXPERIMENTAL RESULTS - AI PERFORMANCE EVALUATION")
        lines.append("="*80)
        lines.append("")
        
        # Header
        header = f"{'Opponent':<22} {'Win Rate':>10} {'Profit':>10} {'ROI':>10} {'Hands':>8} {'Time/Dec':>10}"
        lines.append(header)
        lines.append("-"*80)
        
        # Data rows
        for result in self.results:
            opp = result['opponent_name']
            win_rate = result['ai_win_rate']
            profit = result['profit']
            roi = result['roi']
            hands = result['hands_played']
            time = result['avg_decision_time']
            
            row = f"{opp:<22} {win_rate:>10} {profit:>10d} {roi:>10} {hands:>8} {time:>10}"
            lines.append(row)
        
        lines.append("="*80)
        
        # Add analysis
        lines.append("")
        lines.append("ANALYSIS:")
        lines.append("-"*80)
        
        # Calculate aggregates
        total_hands = sum(r['hands_played'] for r in self.results)
        total_wins = sum(r['hands_won_by_ai'] for r in self.results)
        avg_win_rate = (total_wins / total_hands * 100) if total_hands > 0 else 0
        
        lines.append(f"Total hands played: {total_hands}")
        lines.append(f"Overall win rate: {avg_win_rate:.1f}%")
        
        # Best/worst matchups
        best = max(self.results, key=lambda r: float(r['ai_win_rate'].rstrip('%')))
        worst = min(self.results, key=lambda r: float(r['ai_win_rate'].rstrip('%')))
        
        lines.append(f"Best matchup: {best['opponent_name']} ({best['ai_win_rate']} win rate)")
        lines.append(f"Worst matchup: {worst['opponent_name']} ({worst['ai_win_rate']} win rate)")
        
        # Most profitable
        most_profitable = max(self.results, key=lambda r: r['profit'])
        lines.append(f"Most profitable: {most_profitable['opponent_name']} ({most_profitable['profit']:+d} chips)")
        
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def generate_csv(self, filename: str = "results.csv"):
        """Generate CSV file for Excel/spreadsheet analysis"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            fieldnames = ['Opponent', 'Win_Rate', 'Profit', 'ROI', 'Hands_Played',
                         'Hands_Won', 'Hands_Lost', 'Avg_Decision_Time', 'Total_Decisions']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow({
                    'Opponent': result['opponent_name'],
                    'Win_Rate': result['ai_win_rate'],
                    'Profit': result['profit'],
                    'ROI': result['roi'],
                    'Hands_Played': result['hands_played'],
                    'Hands_Won': result['hands_won_by_ai'],
                    'Hands_Lost': result['hands_won_by_opponent'],
                    'Avg_Decision_Time': result['avg_decision_time'],
                    'Total_Decisions': result['total_decisions']
                })
        
        print(f"CSV saved to: {filename}")
    
    def generate_full_report(self, output_file: str = "experimental_report.txt"):
        """Generate comprehensive text report"""
        report = []
        
        report.append("="*80)
        report.append("EXPECTIMINIMAX AI - EXPERIMENTAL VALIDATION REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Data from: {self.timestamp}")
        report.append("")
        
        # Configuration
        report.append("CONFIGURATION:")
        report.append("-"*80)
        report.append("Algorithm: Expectiminimax with Monte Carlo evaluation")
        report.append("Search depth: 2 levels")
        report.append("Monte Carlo simulations: 500 per leaf node")
        report.append("Chance node sampling: 8 cards per chance node")
        report.append("Action abstraction: 4-7 actions per state")
        report.append("")
        
        # Results table
        report.append(self.generate_ascii_table())
        report.append("")
        
        # Detailed analysis for each opponent
        report.append("DETAILED OPPONENT ANALYSIS:")
        report.append("="*80)
        report.append("")
        
        for result in self.results:
            report.append(f"--- {result['opponent_name']} ---")
            report.append(f"Strategy: {self._get_opponent_description(result['opponent_name'])}")
            report.append(f"Win rate: {result['ai_win_rate']}")
            report.append(f"Profit: {result['profit']:+d} chips")
            report.append(f"ROI: {result['roi']}")
            report.append(f"Hands played: {result['hands_played']}")
            report.append(f"Largest pot won: {result['largest_pot_won']} chips")
            report.append(f"Largest pot lost: {result['largest_pot_lost']} chips")
            report.append(f"Average decision time: {result['avg_decision_time']}")
            report.append("")
        
        # Conclusions
        report.append("CONCLUSIONS:")
        report.append("="*80)
        report.append(self._generate_conclusions())
        report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write("\n".join(report))
        
        print(f"Full report saved to: {output_file}")
        
        return "\n".join(report)
    
    def _get_opponent_description(self, opponent_name: str) -> str:
        """Get description of opponent strategy"""
        descriptions = {
            "Calling Station": "Never folds, always calls. Most exploitable.",
            "Aggressive Player": "Always bets/raises. High pressure strategy.",
            "Tight Player": "Folds frequently, only plays strong hands.",
            "Random Player": "Makes random decisions. Baseline comparison.",
            "Passive Player": "Never raises, folds to large bets."
        }
        return descriptions.get(opponent_name, "Unknown strategy")
    
    def _generate_conclusions(self) -> str:
        """Generate conclusions based on results"""
        conclusions = []
        
        # Calculate stats
        win_rates = [float(r['ai_win_rate'].rstrip('%')) for r in self.results]
        avg_win_rate = sum(win_rates) / len(win_rates)
        
        conclusions.append(f"1. Overall Performance: AI achieved {avg_win_rate:.1f}% average win rate")
        conclusions.append("   across all opponent types, demonstrating robust performance.")
        conclusions.append("")
        
        # Best matchup analysis
        best = max(self.results, key=lambda r: float(r['ai_win_rate'].rstrip('%')))
        conclusions.append(f"2. Best Performance: Against {best['opponent_name']} ({best['ai_win_rate']}),")
        conclusions.append("   showing AI effectively exploits predictable strategies.")
        conclusions.append("")
        
        # Worst matchup analysis
        worst = min(self.results, key=lambda r: float(r['ai_win_rate'].rstrip('%')))
        conclusions.append(f"3. Challenging Matchup: {worst['opponent_name']} ({worst['ai_win_rate']})")
        conclusions.append("   presents the most difficulty, likely due to defensive play")
        conclusions.append("   that minimizes exploitable patterns.")
        conclusions.append("")
        
        # Profitability
        total_profit = sum(r['profit'] for r in self.results)
        conclusions.append(f"4. Profitability: Total profit of {total_profit:+d} chips demonstrates")
        conclusions.append("   the AI's ability to accumulate value over time.")
        conclusions.append("")
        
        # Performance
        avg_time = sum(float(r['avg_decision_time'].rstrip('s')) for r in self.results) / len(self.results)
        conclusions.append(f"5. Computational Efficiency: Average decision time of {avg_time:.3f}s")
        conclusions.append("   is acceptable for real-time play, balancing depth with speed.")
        
        return "\n".join(conclusions)


# Standalone usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <results_file.json>")
        print("\nOr generate sample report from most recent results...")
        
        # Try to find most recent results file
        import glob
        files = glob.glob("experiment_results_*.json")
        if files:
            latest = max(files)
            print(f"Found: {latest}")
            results_file = latest
        else:
            print("No results files found. Run experimental_suite.py first.")
            sys.exit(1)
    else:
        results_file = sys.argv[1]
    
    # Generate reports
    generator = ReportGenerator(results_file)
    
    print("Generating reports...")
    print()
    
    # ASCII table (console)
    print(generator.generate_ascii_table())
    print()
    
    # Full report
    generator.generate_full_report()
    
    # CSV for analysis
    generator.generate_csv()
    
    # Markdown for README
    with open("results_table.md", 'w') as f:
        f.write(generator.generate_markdown_table())
    print("Markdown table saved to: results_table.md")
    
    # LaTeX for academic paper
    with open("results_table.tex", 'w') as f:
        f.write(generator.generate_latex_table())
    print("LaTeX table saved to: results_table.tex")
    
    print("\nAll reports generated successfully!")