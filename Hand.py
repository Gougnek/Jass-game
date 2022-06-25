""" This file is part of a sample of the swiss Jass game implementation

    Classes in that file manage objects and methods related to Hand and Handset management
"""

from Deck import Deck
from GameData import GameData
import pygame
from Card import Card

class Hand(Deck):
    """Represents a hand of playing cards and other player-related data."""
    
    def __init__(self, label=''):
        self.cards = []
        self.label = label
        self.KeyCode = ' ' # Key code that the user will use to allow the display of his deck

    def sort(self):
        """Sorts the cards in ascending order, firt suit, then rank."""
        self.cards = sorted(self.cards, key=lambda x: (x.suit, x.rank), reverse=False)
        
    def sortbyrank(self):
        """Sorts the cards in ascending order, based only on rank."""
        self.cards = sorted(self.cards, key=lambda x: x.rank, reverse=False)
    
    def CheckPlayerKey(self, key, GameData):
        """ Check if the key provided is the secret user key"""
        if key == self.KeyCode:
            GameData.key_confirmed = True
        else:
            GameData.key_confirmed = False
        return GameData.key_confirmed

    def test_blitRotate(surf, image, pos, originPos, angle): # For tests
        image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
        surf.blit(rotated_image, rotated_image_rect)

    
    def DisplayRotatedCardPlayer(self, gameBoard, surface, angle, pivot, offset, PlayerNumber):
        """Rotate the surface around the pivot point.

        Args:
            gameBoard (class GameBoard): Class of the display window. Pixels are in .screen element
            surface (pygame.Surface): The surface that is to be rotated.
            angle (float): Rotate by this angle.
            pivot (tuple, list, pygame.math.Vector2): The pivot point.
            offset (pygame.math.Vector2): This vector is added to the pivot.
        """

        xInitial = 200
        yInitial = 180*PlayerNumber + 10   

        rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
        rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
        # Add the offset vector to the center/pivot point to shift the rect.
        rect = rotated_image.get_rect(center=pivot+rotated_offset)

        #Modify rect to display at the original place
        rect = rect.move(xInitial, yInitial)

        # Added: Blit the new picture
        gameBoard.screen.blit(rotated_image, rect)  # Blit the rotated image.

        return rotated_image, rect  # Return the rotated image and shifted rect.


    def show_cards_fan(self, gameBoard, PlayerNumber, Handset, card_picts):
        """Shows cards on the screen"""
        for i in range(len(self.cards)):
            card = Handset.players[PlayerNumber].cards[i]
            # surface = handset.players[PlayerNumber].cards[i].picture
            surface = card_picts.GetCardPicture(card.suit, card.rank)
            
            # Rotate the cards by 13° each around a point  in left-right middle, but below the card, and display it
            Handset.players[PlayerNumber].DisplayRotatedCardPlayer(gameBoard, surface, (i-4)*13, [90//2, 135], pygame.math.Vector2(0, -135//2), PlayerNumber)


    def show_cards(self, gameBoard, PlayerNumber, card_picts):
        """Shows cards on the screen"""
        x,y = gameBoard.HandxShift, 136*PlayerNumber
        NbCards = len(self.cards)
        for i in range(NbCards):
            gameBoard.screen.blit(card_picts.GetCardPicture(self.cards[i].suit, self.cards[i].rank), (x,y))
            x=x+91

    def show_played_cards(self, gameDisplay, card_picts):
        """Shows played cards on the screen"""
        x=0
        # Calculate the number of played cards
        NbCards = len(self.cards)
        for i in range(NbCards):
            gameDisplay.blit(card_picts.GetCardPicture(self.cards[i].suit, self.cards[i].rank), (x,650))
            x=x+45 # move right half of a card

    def show_won_cards(self, gameBoard, deck, team_id, DataGame, card_picts):
        """Shows cards won by the different teams
        
        team_id: 0 or 1 depending on the team to display
        """
        x, y = 10*91, 4*135 + 10 + team_id*135

        #Display name of team before the deck
        textsurface = gameBoard.font.render('Equipe ' + str(team_id + 1), False, (255, 255, 255))
        gameBoard.screen.blit(textsurface, (x - 150, y + 40))

        # Calculate the number of played cards
        NbCards = len(self.cards)
        if NbCards > 4:
            # Display first the background of a card
            gameBoard.screen.blit(card_picts.background_picture, (x-20,y))
            FirstCard = NbCards -4
        else:
            FirstCard = 0
        if DataGame.latest_winner % 2 == team_id: # Only display cards won from team who won the latest
            for i in range(FirstCard, NbCards):
                mypicture = card_picts.GetCardPicture(self.cards[i].suit, self.cards[i].rank)
                gameBoard.screen.blit(mypicture, (x,y))
                x=x+45 # move right half of a card
        else:
            # For the other team, show only a background if cards have already been won
            if NbCards > 0:
                # Display the background of a card
                gameBoard.screen.blit(card_picts.background_picture, (x-20,y))

    def pop_card(self, i=-1):
        """Removes and returns a card from the deck of the player.

        i: index of the card to pop; by default, pops the last card.
        """
        return self.cards.pop(i)

    def add_card(self, card):
        """Adds a card to the deck.

        card: Card
        """
        self.cards.append(card)
    
    def winner_played(self, game_data):
        """Returns who won the set of played cards.
        hand: The hand of played cards
        
        Tests done:
        * Define the mode by checking if an atout exists in the deck
          * If an atout exists, go through using the "GetAtoutCorrectedRange" function to compare in atout mode
          * If no atout exists, go through using standard comparison
        
        """
        # Check that the quantity of cards is coherent
        if len(self.cards) != game_data.nbplayers:
            return -1
        
        AtoutPresent = False
        MaxValue = -1
        # Check atout presence
        for obj in self.cards:
            if (obj.suit == game_data.atout):
                AtoutPresent = True
        
        if (AtoutPresent):
            for i in range(len(self.cards)):
                if (self.cards[i].suit == game_data.atout):
                    if(MaxValue <= self.cards[i].GetAtoutCorrectedRange()):
                        MaxValue = self.cards[i].GetAtoutCorrectedRange()
                        CurrentWinner = (game_data.current_turn_first_player + i) % game_data.nbplayers
        else: # No atout in the deck
            for i in range(len(self.cards)):
                if (self.cards[i].suit == self.cards[0].suit): # Check that this is the base suit
                    if (MaxValue <= self.cards[i].rank):
                        MaxValue = self.cards[i].rank
                        CurrentWinner = (game_data.current_turn_first_player + i) % game_data.nbplayers

        # Update the information in GameData
        game_data.latest_winner = CurrentWinner
        return CurrentWinner

    def move_cards_won(self, hand_to):
        """ Move the cards to the won pile of the right team
        """
        # First invert the cards to have them in the right order in the end
        self.cards.reverse()
        NbCards = len(self.cards)
        for i in range(NbCards):
            hand_to.add_card(self.pop_card()) # Move the card to the won stock
    
    def check_end_turn_and_move_cards(self, DataGame, TeamWonSet):
        """ Checks if this is then end of the turn. If yes,
        perform actions like moving cards
        """
        if (len(self.cards) >= 4):
            WinnerTeam = self.winner_played(DataGame)
            self.move_cards_won(TeamWonSet.players[WinnerTeam % 2])
            DataGame.SetNextTurnFirstPlayer()
        else:
            DataGame.SetNextPlayer() # Change player number for next turn

    def CheckBetterRow(self, fRowSize, fSuit, fRank, i_card, nRowSize,  DataGame):
        """ Compare found row to existing stored and tell if better. Usually used to check if cards in a row with points exist

        variables starting with "f" are already found rows data
        Variables starting with "n" are new found rows data
        fRowSize: Highest row found until now (usefull to check that new row is longer)
        fSuit: Suit of already found row (not used for the moment, but for improvement to check for example if this was the atout)
        fRank: Max rank of already found row (not used for the moment, but for improvement to check for example if this was the atout)
        i_card: index + 1 of the position of the card to check (+ 1 because we check the value of the row AFTER that the row is finished, so we are 1 card further)
        nRowSize: Number of cards found until now (Ex: if 3 cards are in a row, nRowSize will be 3)

        Returns True if the found row is better than existing one
        """
        Found = False
        nSuit, nRank = -1, -1 # Initiate to dummy values
        # 1. Check if we had at least 3 cards found
                # 2. If yes, check that the highest card (i-1) is better than any previously found suite
                    # If yes, store current suite found (note: The suite may be bigger, we will see that at next iteration)
                    # If No, Don't store anything
        if nRowSize >= 3:
            if nRowSize > fRowSize: # If the new row is longer than any previous one, store infos
                Found = True
                nRank = self.cards[i_card-1].rank
                nSuit = self.cards[i_card-1].suit
            elif nRowSize == fRowSize: # In that case, store only if new row is atout
                if self.cards[i_card-1].suit == DataGame.atout:
                    Found = True
                    nRank = self.cards[i_card-1].rank
                    nSuit = self.cards[i_card-1].suit

        return Found, nRowSize, nSuit, nRank

    def CheckCardsInarow(self, DataGame):
        """ Checks if a 3-in-a-row or more exists

        Args:
            Self (class Hand): Hand of the player to check
            DataGAme (class DataGame): Information about the game
            
        Output:
            * Found True if found
            * fRowSize, fSuit, fRank found (row-size found, suit, followed by rank or highest card)
            
        Prerequisite: Cards in the hand ordered by suit and then rank
        """
        Found = False # Will be true if the searched anonce is found
        fRowSize = -1 # Will contain the length of the row found
        fSuit = -1 # Will contain the suit ID if annonce found
        fRank = -1 # Will contain rank. If several, priority to atout. Otherwise, don't care
        CounterCards = 0 # Will count how many cards are in a row
        PreviousRank, PreviousSuit = -1, -1 # Init with impossible values
        for i in range(len(self.cards)):
            # Check that Suite is same and range higher by one
            if self.cards[i].suit == PreviousSuit and self.cards[i].rank == PreviousRank + 1:
                # Card i is part of a row, need to update counter
                CounterCards = CounterCards + 1 # We have one card more in the row
                PreviousSuit = self.cards[i].suit
                PreviousRank = self.cards[i].rank
            else: # Call function to compare new row (whatever size) which will return if it is better than existing, with associated data
                tmp_Found, tmp_nRowSize, tmp_nSuit, tmp_nRank =  self.CheckBetterRow(fRowSize, fSuit, fRank, i, CounterCards,  DataGame)
                if tmp_Found: # New better row found. Store all data related to that new row
                    Found = True
                    fRank = tmp_nRank
                    fSuit = tmp_nSuit
                    fRowSize = tmp_nRowSize
                    # Nothing to do in else here: we have more than 3 cards, but annonce is lower value than existing
                # No else needed: If we have less than 3 cards, no suit can exist

                # We have finished detecting new winning row, we have more than 3 cards, but value is lower ==> nothing to do
                # In all cases, at the end we store current suit and rank (new card for potential new suite)
                PreviousSuit = self.cards[i].suit
                PreviousRank = self.cards[i].rank
                CounterCards = 1 # Reset counter to 1 (we have 1 card in the suit)

        # We are just out of the for loop, maybe the current found row has to be counted
        tmp_Found, tmp_nRowSize, tmp_nSuit, tmp_nRank =  self.CheckBetterRow(fRowSize, fSuit, fRank, i, CounterCards,  DataGame)
        if tmp_Found: # New better row found. Store all data related to that new row
            Found = True
            fRank = tmp_nRank
            fSuit = tmp_nSuit
            fRowSize = tmp_nRowSize
        
        return Found, fRowSize, fSuit, fRank

    def Check4SameRank(self, DataGame):
        """ Checks if a 4 of same rank (from 9 and above) exists

        Args:
            Self (class Hand): Hand of the player to check
            DataGAme (class DataGame): Information about the game
            
        Output:
            * Found True if found
            * SuitFound, RankFound, Score found (suit, followed by rank)
            
        Output is (when exists) a 4-cards with maximum annonce value. If several exist, the bigger rank based on rank_annonces is used
        """
        Found = False # Will be true if the searched anonce is found
        SuitFound = -1 # Will contain MaxRow if annonce found
        RankFound = -1 # Will contain rank. If several, priority to atout. Otherwise, don't care
        ScoreFound = 0 # Will containt the score of the best 4-cards set found
        CurrentMaxScore = 0 # Will contain maximum score found
        CounterCards = 0 # Will count how many cards are in a row
        PreviousRank, PreviousSuit = -1, -1 # Init with impossible values
        
        # Ideally: Re-sort cards by Rank only. Create temporary hand for doing that. Cannot use copy because cards contains pictures
        self.sortbyrank() # The list is now sorted by rank only (temporarily)
        
        for i in range(len(self.cards)):
            # Check that Suite is same and range higher
            pcard = self.cards[i-1] # To simplify call on previous card studied
            card = self.cards[i] # To simplify call on current card studied
            if self.cards[i].rank == PreviousRank:
                # Card i is same rank that previous, need to update counter
                CounterCards = CounterCards + 1 # We have one card more in the row
            else: # First card of a new potential same rank (of new after found one previously). Store potential previous same rank values and then reset previous data
                if CounterCards == 4: # We already found 4 cards of same rank
                    # Calculate score of cards found.
                    TmpScore = card.rank_annonces_points[card.rank_annonces.index(card.rank_names[card.rank])]
                    if TmpScore > ScoreFound or (TmpScore >= ScoreFound and card.suit == DataGame.atout): # Better 4-cards found, store the related infos. If atout and same score, take the atout one instead of previous
                        ScoreFound = TmpScore
                        RankFound = card.rank
                        SuiteFound = card.suit
                        Found = True
                    CounterCards = 0 # Reset counter
                else: # Just store the found rank
                    PreviousRank = card.rank
                    CounterCards = 1 # We have one card in the row

        # Restore initial sorting
        self.sort() # The list is now sorted by rank only (temporarily)
        
        return Found, SuitFound, RankFound, ScoreFound


    def CheckAnnoncePlayer (self, PlayerNumber, GameData):
        """ Check the best announce of a player

        Args:
            Self (class Hand): Hand of the player to check "Annonces"
            GameData (Class GameData): Necessary data to chekc annonces
            
        Output:
        * List with:
            * The biggest annonce
            * The total of the annonces
            * The highest card
            * The suit of this highest card 
        """
        Found, fSuit, fRank, TmpScore =  self.Check4SameRank(GameData) # Check best 4-cards that can be found
        FakeCard = self.cards[0] # Just define a fake card to use this object later
        if Found:
            print ("Annonce 4-cards found for player " + str(PlayerNumber) + " in suit " + str(FakeCard.suit_names[fSuit]) + " in rank " + str(FakeCard.rank_names[fRank])) 
        
        Found, fRowSize, fSuit, fRank =  self.CheckCardsInarow(GameData)
        if Found:
            print ("Annonce " + str(fRowSize) + "-row found for player " + str(PlayerNumber) + " in suit " + str(FakeCard.suit_names[fSuit]) + " in rank " + str(FakeCard.rank_names[fRank])) 

class HandSet(Hand):
    """Represents a list of players."""
    
    default_players_names = ["Coralie", "Alain",  "Nathaël", "Sandrine"]
    
    def __init__(self, label=''):
        self.players = []

    def add_Hand(self, hand):
        """Adds a card to the deck.

        card: Card
        """
        self.players.append(hand)
    
    def TestCardExist(self, hand, position):
        """Check if the card exists for the player

        card: Card
        """
        #Get number of cards from the player
        if position < len(hand.cards):
            return True
        return False
    
    def InitializePlayerNames(self, DataGame):
        """ Use fixed list to give name to each player 
        Temporarily, it also defines a key (the plyer number) to allow display of cards"""
        for i in range(DataGame.nbplayers):
             self.players[i].label = self.default_players_names[i]   
             self.players[i].KeyCode = chr(49 + i) # Character '1' is 49 (10-based)


    def IsCardAllowedToBePlayed (self, player, pos_card, played_hand, DataGame):
        """ This function must check if the card selected by the user
        can be played or not, based on jass rules.
        
        Checks:
        * If based color, return that is it OK
        * If atout played, check that it is bigger than existing on played deck
            * If not bigger, check that player had no other option
                * Two cases to manager here: atout-based and not-atout-based
            * Return in any case the answer
        * If not base color check that the player has no more cards of that color and return """
        # First check if this is the same suit as the initial one. If yes, this is OK.
        if len(played_hand.cards) == 0 or played_hand.cards[0].suit == self.players[player].cards[pos_card].suit:
            return True
        if DataGame.atout == self.players[player].cards[pos_card].suit:
            # Player played an atout. Check if the atout is bigger than existing one
            TmpMaxRange = -1
            # Do a loop in oncrease max range until the end of the played cards
            for i in range(len(played_hand.cards)):
                if played_hand.cards[i].GetAtoutCorrectedRange() > TmpMaxRange:
                    if DataGame.atout == played_hand.cards[i].suit: # The card to compare to is an atout
                        TmpMaxRange = played_hand.cards[i].GetAtoutCorrectedRange()
            if TmpMaxRange >= self.players[player].cards[pos_card].rank: # There is a card of higher value before
                # To be verified: if the player didn't have the choice or not
                return False
            else:
                return True # Atout of higher value, is allowed
        # If we are here, this is not an atout, and not the initial colors
        # So we have to check that the player didn't have another choice. Add a condition to be sure
        if played_hand.cards[0].suit != self.players[player].cards[pos_card].suit and DataGame.atout != self.players[player].cards[pos_card].suit:
            # Check that the player has no card of initial suit
            for i in range(len(self.players[player].cards)):
                if i != pos_card: # Skip the card that the player wanted to play
                    if self.players[player].cards[i].suit == played_hand.cards[0].suit and not (self.players[player].cards[i].suit == DataGame.atout and self.players[player].cards[i].rank == self.players[player].cards[i].rank_names.index("Valet")) :
                        return False
            # End of the for loop, this means that no initial suite has been found, so we gan give green light
            return True    
        print ("Warning: No predefined situation for card validation found. Give green light by default")
        return True # Default case that should normally never happen

    def action_play_card(self, pos_card, played_deck, TeamWonSet, DataGame):
        """ Get the card at pos_card from the player hand, and mot it to the played deck. Potentially also moves the cards to the TeamWonSet """
        myCard = self.players[DataGame.current_player].pop_card(pos_card)
        played_deck.add_card(myCard)
        played_deck.check_end_turn_and_move_cards(DataGame, TeamWonSet)
        # Do actions that are only necessary when playing standalone
        if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Standalone"):
            # TODO:  Set background back to green. Issue: missing access to GameBoard class
            if DataGame.preferences.LockDisplay:
                DataGame.key_confirmed = False # Invalidate user

    def action_card_selected(self, player, pos_card, DataGame, played_deck, ScreenGame, TeamWonSet):
        """ If found, select the atout or move card depending on game state, or send info to server

        Return: True if everything could be executed. False if for any reason is was not possible to execute the action

        Note: The return value is used mainly in server mode to say the call function that the action was refused
        """
        WasActionDone = False # Flag to know at the end if we could use the selected card and execute the action, or not.

        if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Client"):
            Con = DataGame.cli_connection
            Con.cli_send_card_selected(pos_card) # Send the selected card to server. Issue: I don't have the connection infos... to call the object
            Con.state = Con.CliStates.index("WaitServer") # Change state so that the client will then wait for server feed-back
            return True # Stop here: we did the job by informing the server
        else:
            if DataGame.state == DataGame.GameStates.index("Play"): # We are in play mode, so select atout or chybre
                if self.IsCardAllowedToBePlayed(player, pos_card, played_deck, DataGame): # Check that card is allowed in the context
                    self.action_play_card(pos_card, played_deck, TeamWonSet, DataGame)
                    if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Standalone"):
                        DataGame.ErrorState = DataGame.ErrorStates.index("NoError")
                        # ScreenGame.BackgroundColor = ScreenGame.BackgroundColorOk
                        print ("Hand action_card_selected OK")
                    WasActionDone = True
                else:
                    # If se are in standalone mode OR server mode, AND player 0, add some graphical effect to show that card is refused
                    if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Standalone") or \
                                (DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Server") and DataGame.current_player == 0):
                        DataGame.ErrorState = DataGame.ErrorStates.index("NotAllowed")
                        # ScreenGame.BackgroundColor = ScreenGame.BackgroundColorError # RED
                        print ("Hand action_card_selected Error")
                    WasActionDone = False
            
            if DataGame.state == DataGame.GameStates.index("SelAtout") or DataGame.state == DataGame.GameStates.index("SelAtoutChibre"): # We are in init, so select atout or chibre
                DataGame.atout = self.players[player].cards[pos_card].suit # select atout
                WasActionDone = True
                if DataGame.state == DataGame.GameStates.index("SelAtoutChibre"):
                    # Need to restore initial player
                    DataGame.current_player = (DataGame.current_player + 2) % 4 # Define other player in team as current player
                if DataGame.preferences.LockDisplay:
                    DataGame.key_confirmed = False # Invalidate user
                self.CheckAnnoncesGame(DataGame) # Now that atout has been chose, check all annonces
                DataGame.state = DataGame.GameStates.index("Play") # Change State to Play
        
        return WasActionDone


    def Inital_game_first_player(self, DataGame):
        """ Look for the 7 of Carreau to define who should start
        """
        for i in range(len(self.players)): # Loop trought the players and their cards until I find the 7 of Carreau
            for j in range(len(self.players[i].cards)):
                if self.players[i].cards[j].rank == self.players[i].cards[j].rank_names.index("7") and \
                self.players[i].cards[j].suit == self.players[i].cards[j].suit_names.index("Carreau"):
                    DataGame.set_current_turn_first_player(i) # Record for player for the turn
                    DataGame.set_current_player(i) # Record current player
                    DataGame.current_first_player_set = i

    def Reset(self, DataGame):
        """ This reset must be called before the Game reset
        """
        for i in range(len(self.players)):
            self.players[i].cards = [] 

    def CheckAnnoncesGame(self, GameData):
        """
        
        Input:
        * self: The handset of all players
        * GameData: Data of the game (nb player, 1st player, atout)
        
        Output:
        * Team who has the best annonce , Total score of all annonces of the team
        """
        for i in range(len(self.players)): # Loop trought the players 
            self.players[i].CheckAnnoncePlayer (i, GameData)
            
        # TODO: Write the real expected output