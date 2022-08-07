""" This file is part of a sample of the swiss Jass game implementation

    Classes in that file manage objects and methods related to a card and the pictures related to the cards
"""

import pygame
from pathlib import Path

class CardPicture:
    """ One object per card, containing suit, rank, foreground picture and background picture
    
    Attributes:
      suit: integer 0-3
      rank: integer 0-9
    """
    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank
        
        PictureFileName = Card.rank_names_file[self.rank] + str(self.suit + 1) + '.png'
        try:
            self.picture = pygame.image.load(Path("Pictures/cards/") / PictureFileName)
        except:
            mypath = "Pictures/cards/" + PictureFileName
            print(mypath + " not found.")

class CardsPictures:
    """ Stores the cards picture outside of the card class for an easier exchange of cards infos in client/server mode.
    
    Attributes:
      suit: integer 0-3
      rank: integer 0-9
    """
    
    def __init__(self):
        # Create a list with cards infos and pictures
        self.card_pict = []
        for suit in range(4):
            for rank in range(0, 9):
                card_pict = CardPicture(suit, rank)
                self.card_pict.append(card_pict)
        
        # Add Background picture
        try:
            self.background_picture = pygame.image.load(Path("Pictures/cards/Back/back1.png"))
        except:
            print("Pictures/cards/Back/Back1.png not found.")
            
    def GetCardPicture(self, suit, rank):
        # Do a search int he list of cards and return the picture
        for i in range(36): # Assumt this is a 36 cards game. Then search for the right rank and suit
            if self.card_pict[i].suit == suit and self.card_pict[i].rank == rank:
                return self.card_pict[i].picture
        # Return null if not found
        return 0

class Card:
    """Represents a standard playing card.
    
    Attributes:
      suit: integer 0-3
      rank: integer 0-9
    """

    suit_names = ["Trèfle", "Coeur", "Pique", "Carreau"]
    rank_names = ["6", "7", "8", "9", "10", "Valet", "Reine", "Roi", "As"] # Suit from lower strength to higher
    rank_names_atout = ["6", "7", "8", "10", "Reine", "Roi", "As",  "9", "Valet"] # Suit from lower strength to higher for atout
    rank_annonces = ["6", "7", "8", "9", "10", "Reine", "Roi", "As",  "9", "Valet"] # Order of points for 4cards annonces
    rank_annonces_points = [0, 0, 0, 0, 100, 100, 100, 100,  150, 200] # Order of points for 4-cards annonces
    rank_names_file = ["six", "seven", "eight", "nine", "ten", "jack", "queen", "king", "ace"] # Names used to find the file on the disk to load the picture
    rank_points = [0, 0, 0, 0, 10, 2, 3, 4, 11] # Points of the cards except atout
    rank_points_atout = [0, 0, 0, 14, 10, 20, 3, 4, 11] # Point of the atout cards
    
    # Following lines are tenative to replace some lists by dictionaries
    # Usage example: RankStrength['7'] will return 1 
    RankStrength = {'6' : 0, '7': 1, '8': 2, '9' : 3, '10' : 4, 'Valet' : 5, 'Reine' : 6, 'Roi' : 7, 'As' : 8 } # Cards strength for comparison
    RankStrengthAtout = {"6" : 0, "7" : 1, "8" : 2, "10" : 3, "Reine" : 4, "Roi" : 5, "As" : 6,  "9" : 7 , "Valet" : 8}  # Cards strength for comparison (Atout)
    RankPoints = {'6' : 0, '7': 0, '8': 0, '9' : 0, '10' : 10, 'Valet' : 2, 'Reine' : 3, 'Roi' : 4, 'As' : 11 }  # Points for final score calculation
    RankPointsAtout = {'6' : 0, '7': 0, '8': 0, '9' : 14, '10' : 10, 'Valet' : 20, 'Reine' : 3, 'Roi' : 4, 'As' : 11 } # Points for final score calculation (Atout)
    RankAnnoncesPoints = {"6" : 0, "7" : 0, "8": 0, "9" : 0, "10" : 100, "Valet" : 200, "Reine" : 100, "Roi" : 100, "As" : 200} # Points for 4-cards annonces
    


    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank
        
        """ PictureFileName = self.rank_names_file[self.rank] + str(self.suit + 1) + '.png'
        try:
            self.picture = pygame.image.load(Path("cards/") / PictureFileName)
        except:
            mypath = "cards/" + PictureFileName
            print(mypath + " not found.") """

    def __str__(self):
        """Returns a human-readable string representation."""
        return '%s de %s' % (Card.rank_names[self.rank],
                             Card.suit_names[self.suit])

    def __lt__(self, other):
        """Compares this card to other, first by suit, then rank.

        returns: boolean
        """
        t1 = self.suit, self.rank
        t2 = other.suit, other.rank
        return t1 < t2

    def GetAtoutCorrectedRange(self):
        """ Modifies the value of the card in order to represent atout values
        Modifications : Move from rank_names values to rank_names_atout values
        """
        # Get list ID (self.rank), get its name, and uset his name to retrieve position in rank_names_atout
        AtoutRange = self.rank_names_atout.index(self.rank_names[self.rank])
        return AtoutRange

class Atout:
    """Class containing fake cards deck with suit picture only."""
    def __init__(self):
        self.cards = [] # Empty list of cards
        for i in range(1,5):
            card = Card(i-1,0) # Fake cards, from 0 to 3, with filenames from 1 to 4
            filename = 'suit' + str(i) + '.png'
            card.picture = pygame.image.load(Path("Pictures/cards/") / filename)
            self.cards.append(card)