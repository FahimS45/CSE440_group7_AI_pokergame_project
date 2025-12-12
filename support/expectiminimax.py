import random
from abstracts import AbstractAgent
from monte_carlo import evaluate_state_heuristic
from typing import Tuple


class ExpectiminimaxAgent(AbstractAgent):
    """
    AI Agent using Expectiminimax algorithm
    """
    
    def __init__(self, name: str, chips: int, search_depth: int = 3):
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False
        self.search_depth = search_depth

    def _find_player_by_name(self, game_state, name: str):
        """Helper: Find player in game state by name"""
        for player in game_state.players:
            if player.name == name:
                return player
        return None
    
    def make_decision(self, game_state) -> Tuple[str, int]:
        """
        Main entry point - called by game manager
        Uses Expectiminimax to choose best action
        
        Returns:
            Tuple of (action, amount) where:
            - action: 'fold', 'check', 'call', 'raise'
            - amount: 0 for fold/check/call, total bet amount for raise
        """
        best_action, best_value = self.expectiminimax_search(game_state)
        return best_action  # Return the full tuple
    
    def expectiminimax_search(self, game_state):
        """Root of search tree"""
        ai_player = self._find_player_by_name(game_state, self.name)
        legal_actions = game_state.get_legal_actions(ai_player)
        
        # If only one action, return it immediately
        if len(legal_actions) == 1:
            return legal_actions[0], 0
        
        best_action = None
        best_value = float('-inf')
        
        for action, amount in legal_actions:
            # Clone state
            new_state = game_state.clone()
            
            # Apply action
            ai_in_new_state = self._find_player_by_name(new_state, self.name)
            new_state.apply_action(ai_in_new_state, action, amount)
            
            # Evaluate resulting state
            value = self.expectiminimax(new_state, self.search_depth - 1, 'MIN')
            
            if value > best_value:
                best_value = value
                best_action = (action, amount)
        
        return best_action, best_value
    
    def expectiminimax(self, game_state, depth, node_type):
        """
        Recursive Expectiminimax
        
        node_type: 'MAX' (AI), 'MIN' (opponent), 'CHANCE' (cards)
        """
        
        # Base case 1: Terminal state
        if game_state.is_terminal():
            return self.evaluate_terminal(game_state)
        
        # Base case 2: Depth limit
        if depth == 0:
            ai_in_state = self._find_player_by_name(game_state, self.name)
            return evaluate_state_heuristic(game_state, ai_in_state)
        
        # Recursive cases
        if node_type == 'MAX':
            return self.max_node(game_state, depth)
        elif node_type == 'MIN':
            return self.min_node(game_state, depth)
        elif node_type == 'CHANCE':
            return self.chance_node(game_state, depth)
    
    def max_node(self, game_state, depth):
        """AI's turn - maximize value"""
        ai_in_state = self._find_player_by_name(game_state, self.name)
        legal_actions = game_state.get_legal_actions(ai_in_state)
        
        max_value = float('-inf')
        
        for action, amount in legal_actions:
            new_state = game_state.clone()
            ai_clone = self._find_player_by_name(new_state, self.name)
            new_state.apply_action(ai_clone, action, amount)
            
            # Determine next node type
            if action == 'fold':
                value = self.evaluate_terminal(new_state)
            else:
                new_state.next_player()
                value = self.expectiminimax(new_state, depth - 1, 'MIN')
            
            max_value = max(max_value, value)
        
        return max_value
    
    def min_node(self, game_state, depth):
        """Opponent's turn - minimize AI's value"""
        current_player = game_state.get_current_player()
        legal_actions = game_state.get_legal_actions(current_player)
        
        min_value = float('inf')
        
        for action, amount in legal_actions:
            new_state = game_state.clone()
            opp_clone = new_state.get_current_player()
            new_state.apply_action(opp_clone, action, amount)
            
            # Check if betting round complete
            if new_state.is_betting_round_complete():
                # Advance to next stage (deal cards)
                value = self.expectiminimax(new_state, depth - 1, 'CHANCE')
            else:
                new_state.next_player()
                # Determine next node type
                next_player = new_state.get_current_player()
                if next_player.name == self.name:
                    next_type = 'MAX'
                else:
                    next_type = 'MIN'
                value = self.expectiminimax(new_state, depth - 1, next_type)
            
            min_value = min(min_value, value)
        
        return min_value
    
    def chance_node(self, game_state, depth):
        """
        Card dealing - compute expected value
        FIXED: Properly deals flop (3 cards), turn (1 card), river (1 card)
        """
        
        remaining_cards = game_state.get_remaining_deck_cards()
        
        # Determine how many cards to deal
        if game_state.betting_round == 'preflop':
            cards_to_deal = 3  # Flop = 3 cards
            next_round = 'flop'
        elif game_state.betting_round == 'flop':
            cards_to_deal = 1  # Turn = 1 card
            next_round = 'turn'
        elif game_state.betting_round == 'turn':
            cards_to_deal = 1  # River = 1 card
            next_round = 'river'
        else:
            # Already at river or beyond
            return self.expectiminimax(game_state, depth - 1, 'MAX')
        
        # Sample possible card combinations
        if len(remaining_cards) < cards_to_deal:
            # Not enough cards - shouldn't happen
            return self.expectiminimax(game_state, depth - 1, 'MAX')
        
        # Sample multiple possible board outcomes
        # For flop: sample different 3-card combinations
        # For turn/river: sample different single cards
        num_samples = min(30, len(remaining_cards) // cards_to_deal)
        
        total_value = 0
        valid_samples = 0
        
        for _ in range(num_samples):
            new_state = game_state.clone()
            
            # Deal the appropriate number of cards
            sampled_cards = random.sample(remaining_cards, cards_to_deal)
            new_state.community_cards.extend(sampled_cards)
            new_state.betting_round = next_round
            
            # Reset betting for new round
            new_state.current_bet = 0
            for player in new_state.players:
                player.current_bet = 0
            new_state.players_acted_this_round = set()
            
            # Continue search
            value = self.expectiminimax(new_state, depth - 1, 'MAX')
            total_value += value
            valid_samples += 1
        
        if valid_samples == 0:
            return 0
        
        # Average over samples
        return total_value / valid_samples    
    def evaluate_terminal(self, game_state):
        """Evaluate terminal state - exact outcome"""
        active_players = game_state.get_active_players()
        
        if len(active_players) == 1:
            winner = active_players[0]
            if winner.name == self.name:
                return game_state.pot  # AI wins
            else:
                return -self.current_bet  # AI loses
        
        # Showdown - compare hands (simplified - use heuristic)
        ai_in_state = self._find_player_by_name(game_state, self.name)
        return evaluate_state_heuristic(game_state, ai_in_state)
    
    # Implement other AbstractPlayer methods
    def update_stack(self, amount: int):
        self.chips += amount
    
    def reset_hand(self):
        self.cards = []
        self.current_bet = 0
        self.folded = False
    
    # AbstractAgent methods (placeholders)
    def act(self, game_state):
        return self.make_decision(game_state)
    
    def evaluate_state(self, game_state) -> float:
        return evaluate_state_heuristic(game_state, self)
    
    def observe(self, game_state, action: str, reward: float):
        pass  # Not needed for Expectiminimax