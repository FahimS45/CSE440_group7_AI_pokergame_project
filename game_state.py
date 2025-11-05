# game_state.py

from abstracts import AbstractGameState

class GameState(AbstractGameState):
    def __init__(self, players):
        self.players = players                # list of Player objects
        self.community_cards = []             # shared cards on the table
        self.pot = 0                          # total chips in the pot
        self.current_bet = 0                  # highest bet this round
        self.phase = "pre-flop"               # game phase
        self.active_player_index = 0          # whose turn it is

    def next_player(self):
        """Move to the next player's turn."""
        self.active_player_index = (self.active_player_index + 1) % len(self.players)

    def reset_round(self):
        """Reset values between rounds (e.g., after a showdown)."""
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.phase = "pre-flop"
