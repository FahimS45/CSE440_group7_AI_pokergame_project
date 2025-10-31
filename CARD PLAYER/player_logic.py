# player_logic.py
from abstracts import AbstractPlayer

# --------- Player Class Implementation ---------
class Player(AbstractPlayer):
    def __init__(self, name: str, chips: int) -> None:
        self.name = name
        self.chips = chips
        self.cards = []
        self.current_bet = 0
        self.folded = False

    def make_decision(self, game_state) -> str:
        """
        Simple decision logic:
        - If no game_state provided → check
        - If there is a bet to call → call
        - Otherwise → check
        """
        if not game_state:  # None or empty dict
            return "check"

        to_call = game_state.get("current_bet", 0) - self.current_bet
        if to_call > 0 and self.chips >= to_call:
            return "call"
        return "check"

    def update_stack(self, amount: int):
        """Update player's chips by adding/subtracting amount"""
        self.chips += amount

    def reset_hand(self):
        """Reset player's hand and bet status for new round"""
        self.cards = []
        self.current_bet = 0
        self.folded = False

    def __repr__(self):
        return f"<Player {self.name}: Chips={self.chips}, Bet={self.current_bet}, Folded={self.folded}>"

# --------- Temporary Placeholder Deck for Testing ---------
class Deck:
    def __init__(self):
        self.cards = [("Hearts", "A"), ("Hearts", "K"),
                      ("Spades", "A"), ("Spades", "K")]
    
    def shuffle(self):
        # placeholder: no shuffle needed for testing
        pass
    
    def deal(self, num_cards):
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards

# --------- Testing Player Class ---------
if __name__ == "__main__":
    # Create test player
    player1 = Player("Alice", 1000)
    
    # Give cards from placeholder Deck
    deck = Deck()
    player1.cards = deck.deal(2)
    
    print(f"Player: {player1.name}, Chips: {player1.chips}, Cards: {player1.cards}")

    # Test make_decision with None game_state
    action = player1.make_decision(game_state=None)
    print("Decision with None game_state:", action)

    # Test make_decision with a current bet
    game_state = {"current_bet": 50}
    action = player1.make_decision(game_state=game_state)
    print("Decision with current_bet=50:", action)

    # Test updating chips
    player1.update_stack(-50)
    print(f"After betting 50 chips: {player1}")

    # Test reset_hand
    player1.reset_hand()
    print(f"After reset: {player1}")
