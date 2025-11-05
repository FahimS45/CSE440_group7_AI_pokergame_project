class Deck:
    def __init__(self):
        self.cards = [("Hearts", "A"), ("Spades", "K")]

    def shuffle(self):
        pass

    def deal(self, num_cards):
        return self.cards[:num_cards]