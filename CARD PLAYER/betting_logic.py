# betting_logic.py
from typing import List
from player_logic import Player

# --------- Betting Round Class ---------
class BettingRound:
    def __init__(self, players: List[Player], pot: int = 0, min_bet: int = 10):
        self.players = players
        self.pot = pot
        self.min_bet = min_bet
        self.current_bet = 0

    def play_round(self):
        """Run one betting round"""
        print("\n--- Betting Round ---")
        for player in self.players:
            if player.folded:
                continue

            # Create simple game_state
            game_state = {"current_bet": self.current_bet}
            action = player.make_decision(game_state)

            if action == "fold":
                player.folded = True
                print(f"{player.name} folds.")
            elif action == "check":
                print(f"{player.name} checks.")
            elif action == "call":
                to_call = self.current_bet - player.current_bet
                self._bet(player, to_call)
                print(f"{player.name} calls {to_call}.")
            elif action == "raise":
                raise_amount = self.min_bet
                self.current_bet += raise_amount
                self._bet(player, self.current_bet)
                print(f"{player.name} raises to {self.current_bet}.")

        print(f"Pot after round: {self.pot}")

    def _bet(self, player: Player, amount: int):
        actual_bet = min(amount, player.chips)
        player.chips -= actual_bet
        player.current_bet += actual_bet
        self.pot += actual_bet

# --------- Test / Demo ---------
if __name__ == "__main__":
    # Create 3 test players
    players = [Player("Alice", 1000), Player("Bob", 1000), Player("Charlie", 1000)]

    # Show initial state
    print("Initial Player States:")
    for p in players:
        print(p)

    # Run a betting round
    betting_round = BettingRound(players)
    betting_round.play_round()

    # Show final state
    print("\nFinal Player States:")
    for p in players:
        print(p)

    print("Total Pot:", betting_round.pot)