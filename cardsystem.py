from abstracts import AbstractCardSystem

import random
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Tuple

# --- 2. Your Helper Classes (Suit, Rank, Card) ---
# This is your original code, unchanged.

class Suit(Enum):
    """Card suits"""
    HEARTS = 'H'
    DIAMONDS = 'D'
    CLUBS = 'C'
    SPADES = 'S'

class Rank(Enum):
    """Card ranks with their values"""
    TWO = (2, '2')
    THREE = (3, '3')
    FOUR = (4, '4')
    FIVE = (5, '5')
    SIX = (6, '6')
    SEVEN = (7, '7')
    EIGHT = (8, '8')
    NINE = (9, '9')
    TEN = (10, '10')
    JACK = (11, 'J')
    QUEEN = (12, 'Q')
    KING = (13, 'K')
    ACE = (14, 'A')
    
    def __init__(self, numeric_value, display):
        self.numeric_value = numeric_value 
        self.display = display




class Card:
    """Represents a single playing card"""
    
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank.display}{self.suit.value}"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __lt__(self, other):
        """For sorting cards"""
        return self.rank.value < other.rank.value

# --- 3. The Concrete Implementation ---
# This is your Deck class, "joined" with the AbstractCardSystem.




class Deck(AbstractCardSystem):
    """
    Represents a deck of 52 playing cards.
    This class implements the AbstractCardSystem.
    """
    
    def __init__(self):
        """
        Implements the abstract __init__ method.
        Creates a fresh deck of 52 cards.
        """
        super().__init__()
        self.cards: List[Card] = []
        self.reset()
    
    def reset(self):
        """Helper method to create a fresh deck of 52 cards"""
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]
    
    def shuffle(self):
        """
        Implements the abstract shuffle method.
        Shuffles the deck.
        """
        random.shuffle(self.cards)



    
    def deal(self, num_cards: int) -> List[Tuple[str, str]]:
        """
        Implements the abstract deal method.
        
        Deals cards from the deck.
        Returns a list of card strings (e.g.[(AS),(KH), '10C'])
        """

        if num_cards > len(self.cards):
            raise ValueError(f"Cannot deal {num_cards} cards. Only {len(self.cards)} left.")
        
        # Pop the Card and convert to string format

        dealt_cards = []
        for _ in range(num_cards):
           card = self.cards.pop()
           dealt_cards.append(card.to.string())
           return dealt_cards
            
        # Convert the List[Card] to the required List[Tuple[str, str]]
        # This formatting step is the key change to match the abstract method
        formatted_hand = [
            (card.rank.display, card.suit.value) 
            for card in dealt_card_objects
        ]
        
        return formatted_hand
    

    
    
    def cards_remaining(self) -> int:
        """A helper method specific to this Deck class"""
        return len(self.cards)
    
    def __str__(self):
        return f"Deck with {len(self.cards)} cards"


