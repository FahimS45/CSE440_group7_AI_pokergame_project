# game_manager.py
from player_logic import Player
from betting_logic import BettingRound
from mock_support import MockCardSystem, MockHandEvaluator
import random

class GameManager:
    def __init__(self):
        # Create mock card and evaluation systems
        self.card_system = MockCardSystem()
        self.hand_evaluator = MockHandEvaluator()

        # Create players
        self.players = [
            Player("Alice", 1000),
            Player("Bob", 1000),
            Player("Charlie", 1000)
        ]

        self.pot = 0

    # ---------- Setup ----------
    def start_game(self):
        print("\n===== POKER GAME SIMULATION (SPRINT 1 DEMO) =====")
        self.card_system.shuffle()

        # Deal 2 cards to each player
        for player in self.players:
            player.cards = self.card_system.deal(2)
            print(f"{player.name}'s cards: {player.cards}")

        # Run a single betting round
        betting_round = BettingRound(self.players)
        betting_round.play_round()

        self.pot += betting_round.pot
        print(f"\n>>> Total Pot after betting: {self.pot}")

        # Evaluate winner using mock evaluator
        self.declare_winner()

    # ---------- Determine Winner ----------
    def declare_winner(self):
        print("\n--- Evaluating Hands ---")

        scores = {}
        for player in self.players:
            if player.folded:
                continue
            score = self.hand_evaluator.evaluate_hand(player.cards)
            scores[player] = score
            print(f"{player.name} hand score: {score}")

        if not scores:
            print("All players folded. No winner.")
            return

        # Pick the highest mock hand rank
        winner = max(scores, key=lambda p: scores[p][0])
        print(f"\n Winner: {winner.name} wins the pot of {self.pot} chips!")

        # Award pot to winner
        winner.update_stack(self.pot)
        self.pot = 0

        print("\n--- Final Player States ---")
        for p in self.players:
            print(p)

# ---------- Run Demo ----------
if __name__ == "__main__":
    game = GameManager()
    game.start_game()
