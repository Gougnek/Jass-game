""" This file is part of a sample of the swiss Jass game implementation

    Classes in that file manage objects and methods related to the initial Deck
"""

import math, random, pygame
from pathlib import Path
from Card import Card

class Deck:
    """Represents a deck of cards.

    Attributes:
      cards: list of Card objects.
    """
    
    def __init__(self):
        """Initializes the Deck with 36 cards.
        """
        self.cards = []
        for suit in range(4):
            for rank in range(0, 9):
                card = Card(suit, rank)
                self.cards.append(card)


    def __str__(self):
        """Returns a string representation of the deck.
        """
        res = []
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)

    def add_card(self, card):
        """Adds a card to the deck.

        card: Card
        """
        self.cards.append(card)

    def remove_card(self, card):
        """Removes a card from the deck or raises exception if it is not there.
        
        card: Card
        """
        self.cards.remove(card)

    def pop_card(self, i=-1):
        """Removes and returns a card from the deck.

        i: index of the card to pop; by default, pops the last card.
        """
        return self.cards.pop(i)

    def shuffle(self):
        """Shuffles the cards in this deck."""
        random.shuffle(self.cards)

    def sort(self):
        """Sorts the cards in ascending order."""
        self.cards.sorted()


    def move_cards(self, hand, num):
        """Moves the given number of cards from the deck into the Hand.

        hand: destination Hand object
        num: integer number of cards to move
        """
        for i in range(num):
            hand.add_card(self.pop_card())
    
    def distribute_cards(self, handset, DataGame):
            # Distribute the cards
        NbCardsPerPlayer = len(self.cards) // DataGame.nbplayers
        for i in range(DataGame.nbplayers):
            self.move_cards(handset.players[i], NbCardsPerPlayer) # Move cards from deck to handset
            handset.players[i].sort()

    def Reset(self):
        """Re Initializes the Deck with 36 cards.
        """
        #Empty the deck (In case it was not empty)
        if len(self.cards) > 0:
            for i in range(-1, -1*len(self.cards)):
                return self.cards.pop(i)

        # Re-create a new deck
        for suit in range(4):
            for rank in range(0, 9):
                card = Card(suit, rank)
                self.cards.append(card)
        try:
            self.back_picture = pygame.image.load(Path("cards/Back/") / 'back1.png') # Load a background, valid for all cards
        except:
            print("cards/Back/back1.png not found.")

    def ResetForNextSet(self, DataGame, handset, TeamWonSet):
        """ Function to call to reset everything, ready for new set
        This will keep data like scores
        """
        # Reset all data not reusable for the new set
        handset.Reset(DataGame)
        TeamWonSet.Reset(DataGame)
        self.Reset()
        DataGame.Reset()
        # Do other initializations to start new set. Only if standalone or server
        if DataGame.is_this_network_mode("Server") or DataGame.is_this_network_mode("Standalone"):
            self.shuffle() # Shuffle the initial cards
            self.distribute_cards(handset, DataGame)