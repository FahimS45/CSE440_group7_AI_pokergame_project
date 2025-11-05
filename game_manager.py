# game_manager.py

from cards import CardSystem
from hand_evaluator import HandEvaluator
from game_state import GameState

class GameManager:
    def __init__(self, players):
        self.deck = CardSystem()
        self.evaluator = HandEvaluator()
        self.state = GameState(players)

    def start_new_round(self):
        """Start a new hand."""
        self.deck = CardSystem()
        self.deck.shuffle()
        self.state.reset_round()

        # Deal 2 cards to each player
        for player in self.state.players:
            player.reset_hand()
            player.cards = self.deck.deal(2)

        print("\n--- New Round Started ---")
        for p in self.state.players:
            print(f"{p.name} cards: {p.cards}")

        # Start phases
        self.play_phase("pre-flop")
        self.play_phase("flop")
        self.play_phase("turn")
        self.play_phase("river")
        self.showdown()

    def play_phase(self, phase):
        """Simulate a betting phase."""
        self.state.phase = phase

        if phase == "flop":
            self.state.community_cards = self.deck.deal(3)
        elif phase == "turn":
            self.state.community_cards += self.deck.deal(1)
        elif phase == "river":
            self.state.community_cards += self.deck.deal(1)

        print(f"\n== {phase.upper()} ==")
        print(f"Community cards: {self.state.community_cards}")

        # Loop through each player's decision
        for player in self.state.players:
            if player.folded:
                continue
            decision = player.make_decision(self.state)
            print(f"{player.name} -> {decision}")

    def showdown(self):
        """At the end of the round, compare hands."""
        print("\n== SHOWDOWN ==")
        for player in self.state.players:
            if not player.folded:
                print(f"{player.name}: {player.cards} + {self.state.community_cards}")
