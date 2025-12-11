import random
from typing import List
from hand_evaluator import PokerHandEvaluator
from abstracts import AbstractPlayer


class MonteCarloEvaluator:
    """
    Monte Carlo simulator for poker hand strength evaluation.
    BALANCED: 200 simulations for speed, conservative evaluation for better strategy
    """
    
    def __init__(self, num_simulations: int = 1000):
        """
        Initialize Monte Carlo evaluator.
        
        Args:
            num_simulations: Default number of simulations (200 for speed)
        """
        self.evaluator = PokerHandEvaluator()
        self.default_simulations = num_simulations
    
    def simulate_hand_strength(
        self,
        ai_hole_cards: List[str],
        community_cards: List[str],
        remaining_deck: List[str],
        num_simulations: int = None
    ) -> float:
        """
        Estimate AI's win probability through Monte Carlo simulation.
        
        Args:
            ai_hole_cards: AI's 2 hole cards (e.g., ['AS', 'KH'])
            community_cards: Current board (0-5 cards)
            remaining_deck: Cards not yet dealt
            num_simulations: Number of simulations (default: self.default_simulations)
        
        Returns:
            Win probability (0.0 to 1.0)
        """
        if num_simulations is None:
            num_simulations = self.default_simulations
        
        # Validation
        if len(ai_hole_cards) != 2:
            raise ValueError(f"AI must have exactly 2 hole cards, got {len(ai_hole_cards)}")
        
        if len(community_cards) > 5:
            raise ValueError(f"Cannot have more than 5 community cards, got {len(community_cards)}")
        
        if len(remaining_deck) < 2:
            return 0.5  # Default to 50% if can't simulate
        
        wins = 0
        ties = 0
        valid_sims = 0
        
        for _ in range(num_simulations):
            # Clone remaining deck for this simulation
            sim_deck = remaining_deck.copy()
            random.shuffle(sim_deck)
            
            # Complete the board if needed
            cards_needed = 5 - len(community_cards)
            if cards_needed > 0:
                if len(sim_deck) < cards_needed + 2:
                    continue  # Not enough cards
                
                sim_community = community_cards + sim_deck[:cards_needed]
                sim_deck = sim_deck[cards_needed:]
            else:
                sim_community = community_cards
            
            # Deal random opponent cards (2 cards)
            if len(sim_deck) < 2:
                continue
            opponent_cards = sim_deck[:2]
            
            # Evaluate both hands
            ai_full_hand = ai_hole_cards + sim_community
            opp_full_hand = opponent_cards + sim_community
            
            try:
                result = self.evaluator.compare_hands(ai_full_hand, opp_full_hand)
                
                if result == 1:
                    wins += 1
                elif result == 0:
                    ties += 1
                
                valid_sims += 1
            except Exception:
                # If hand evaluation fails, skip this simulation
                continue
        
        # Calculate win rate (ties count as 0.5 wins)
        if valid_sims == 0:
            return 0.5
        
        win_rate = (wins + 0.5 * ties) / valid_sims
        return win_rate
    
    def evaluate_state_heuristic(
        self,
        game_state,
        ai_player: AbstractPlayer
    ) -> float:
        """
        ✅ BALANCED HEURISTIC: Conservative evaluation that encourages strategic play
        
        Key philosophy:
        - Only be aggressive with STRONG hands (win_prob > 0.65)
        - Be cautious with medium hands (0.45 - 0.65)
        - Fold weak hands quickly (win_prob < 0.45)
        - Consider pot odds and cost to continue
        
        Combines multiple factors:
        - Hand strength (via Monte Carlo simulation) - MAIN FACTOR
        - Expected pot value - conservative weighting
        - Cost to continue - significant penalty for expensive calls
        - Position advantage - small bonus
        - Stack depth - risk management
        
        Args:
            game_state: Current game state
            ai_player: The AI player to evaluate for
        
        Returns:
            Expected value in chips (higher = better for AI)
        """
        
        # Get hand strength via Monte Carlo
        try:
            remaining = game_state.get_remaining_deck_cards()
            win_prob = self.simulate_hand_strength(
                ai_player.cards,
                game_state.get_community_cards(),
                remaining,
                num_simulations=self.default_simulations
            )
        except Exception:
            # If simulation fails, default to neutral evaluation
            win_prob = 0.5
        
        # Get game factors
        pot = game_state.get_pot_size()
        current_bet = game_state.get_current_bet()
        
        # Calculate expected pot value
        expected_pot_value = win_prob * pot
        
        # Cost to call (penalty)
        amount_to_call = max(0, current_bet - ai_player.current_bet)
        
        # Position bonus (later position = better)
        position_bonus = self._calculate_position_bonus(game_state, ai_player)
        
        # Stack depth factor
        stack_factor = self._calculate_stack_factor(game_state, ai_player)
        
        # ✅ BALANCED HEURISTIC: Conservative approach
        # Key changes from aggressive version:
        # 1. Lower base value from hand strength (100 instead of 150)
        # 2. Higher threshold for bonuses (0.75 instead of 0.7)
        # 3. Stronger penalties for weak hands
        # 4. Higher penalty for calling (1.8x instead of 1.0x)
        # 5. Lower weight on pot value (1.5x instead of 3.0x)
        
        # Base value from hand strength (reduced)
        hand_strength_value = win_prob * 100
        
        # Bonus ONLY for very strong hands (encourages selective aggression)
        if win_prob > 0.75:
            hand_strength_value += 40  # Strong hands get bonus
        elif win_prob > 0.65:
            hand_strength_value += 20  # Good hands get small bonus
        
        # Penalty for weak/medium-weak hands (encourages folding)
        if win_prob < 0.35:
            hand_strength_value -= 60  # Heavy penalty for weak hands
        elif win_prob < 0.45:
            hand_strength_value -= 30  # Moderate penalty for medium-weak hands
        
        # ✅ POT ODDS CONSIDERATION
        # If cost to call is high relative to pot, add extra penalty
        if pot > 0:
            pot_odds_ratio = amount_to_call / pot
            if pot_odds_ratio > 0.5:  # Calling more than half the pot
                hand_strength_value -= 40  # Extra penalty for bad pot odds
        
        # Final heuristic calculation (BALANCED)
        value = (
            expected_pot_value * 1.5 +       # Conservative pot value weight (was 3.0)
            hand_strength_value +             # Hand strength with bonuses/penalties
            position_bonus +                  # Small position bonus
            stack_factor -                    # Stack considerations
            amount_to_call * 1.8              # Higher call penalty (was 1.0)
        )
        
        return value
    
    def _calculate_position_bonus(self, game_state, ai_player: AbstractPlayer) -> float:
        """
        Calculate position bonus for AI player.
        Later position is better (can see more actions before deciding).
        
        Returns:
            Bonus value (0-12 points typically)
        """
        try:
            num_players = len(game_state.players)
            position_index = game_state.players.index(ai_player)
            button = game_state.button_position
            
            # Distance from button (0 = on button, best position)
            distance_from_button = (position_index - button) % num_players
            
            # Convert to bonus (closer to button = higher bonus)
            # Reduced to 2 per position (minimal influence)
            position_bonus = (num_players - distance_from_button) * 2
            
            return position_bonus
        except Exception:
            return 0  # Default if position can't be calculated
    
    def _calculate_stack_factor(self, game_state, ai_player: AbstractPlayer) -> float:
        """
        Calculate stack depth factor.
        Deep stacks allow more maneuvering room.
        Short stacks require more caution.
        
        Returns:
            Stack factor value (-20 to +15)
        """
        try:
            pot = game_state.get_pot_size()
            if pot == 0:
                return 0
            
            # Stack-to-pot ratio
            stack_pot_ratio = ai_player.chips / pot
            
            # Deep stacks (>10x pot) get small bonus
            if stack_pot_ratio > 10:
                return 15
            # Short stacks (<3x pot) get penalty (need to be more careful)
            elif stack_pot_ratio < 3:
                return -20  # Increased penalty (was -15)
            # Very short stacks (<2x pot) get severe penalty
            elif stack_pot_ratio < 2:
                return -40  # High risk situation
            # Medium stacks (3-10x pot) - neutral
            else:
                return 0
        except Exception:
            return 0


# Convenience functions for easy import and use

def monte_carlo_hand_strength(
    ai_hole_cards: List[str],
    community_cards: List[str],
    remaining_deck: List[str],
    num_simulations: int = 200
) -> float:
    """
    Convenience function for hand strength simulation.
    
    Args:
        ai_hole_cards: AI's 2 hole cards
        community_cards: Current board (0-5 cards)
        remaining_deck: Cards not yet dealt
        num_simulations: Number of simulations to run (default: 200)
    
    Returns:
        Win probability (0.0 to 1.0)
    """
    evaluator = MonteCarloEvaluator(num_simulations=num_simulations)
    return evaluator.simulate_hand_strength(
        ai_hole_cards,
        community_cards,
        remaining_deck
    )


def evaluate_state_heuristic(game_state, ai_player: AbstractPlayer) -> float:
    """
    ✅ BALANCED: Convenience function for state evaluation
    
    Args:
        game_state: Current game state
        ai_player: The AI player to evaluate for
    
    Returns:
        Expected value in chips (higher = better for AI)
    """
    evaluator = MonteCarloEvaluator(num_simulations=5000)
    return evaluator.evaluate_state_heuristic(game_state, ai_player)
