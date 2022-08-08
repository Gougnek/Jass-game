""" This file is part of a sample of the swiss Jass game implementation

    Classes in that file manage objects and methods related to Hand and Handset management
"""

# from site import addsitedir
from Deck import Deck
from GameData import GameData
import pygame, copy
from Card import Card

class Hand(Deck):
    """Represents a hand of playing cards and other player-related data."""
    
    def __init__(self, label=''):
        self.cards = []
        self.label = label
        self.KeyCode = ' ' # Key code that the user will use to allow the display of his deck
        self.annonces = [] # Table to store found annonces during the annonce check. Each position contains a list: [ComparisonPoints, RealPoints, RefCardRank]
        self.stockr = False # Will be true if the Stöckr is found for this player
        self.annonces_cards = [] # Table to store cards from found annonces in order to display them later

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

    def show_cards_debug(self, gameBoard, PlayerNumber, card_picts):
        """Shows cards on the screen on background picture for debug purpose
        
        Note: We assume that the player for which to show the cards
        Card is 136 high, 91 wide. Background size is supposed to be 1152x648

        """
        x,y = 0, 0
        NbCards = len(self.cards)
        for i in range(NbCards):
            gameBoard.screen.blit(card_picts.GetCardPicture(self.cards[i].suit, self.cards[i].rank), (x,PlayerNumber*136))
            x=x+91

    def show_cards(self, gameBoard, PlayerNumber, card_picts):
        """Shows cards on the screen on background picture
        
        Note: We assume that the player for which to show the cards
        Card is 136 high, 91 wide. Background size is supposed to be 1152x648

        """
        x,y = 1152//2 - 410, 648 - 136
        NbCards = len(self.cards)
        for i in range(NbCards):
            gameBoard.screen.blit(card_picts.GetCardPicture(self.cards[i].suit, self.cards[i].rank), (x,y))
            x=x+91

    def show_played_cards(self, gameDisplay, card_picts):
        """Shows played cards on the screen"""
        x,y = 420, 250
        # Calculate the number of played cards
        NbCards = len(self.cards)
        for i in range(NbCards):
            gameDisplay.blit(card_picts.GetCardPicture(self.cards[i].suit, self.cards[i].rank), (x,y))
            x=x+45 # move right half of a card

    def show_played_cards1(self, gameDisplay, card_picts):
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
        x, y = 180 + team_id*400 ,5 

        #Display name of team before the deck
        textsurface = gameBoard.font_big.render('Equipe ' + str(team_id + 1), False, (255, 255, 255))
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

        card: Card to be added
        """
        self.cards.append(card)

    def add_card_annonce(self, card):
        """ Add card poped from temporary deck to the annonce deck

        card: Card to be added
        """
        self.annonces_cards.append(card)
    
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

    def check_stockr(self, DataGame, player):
        """ Checks if the player has the Stöckr and store this information in the hand parameters of the player

        Args:
            Self (class Hand): copied hand of the player to check, or remaining after previous checks
            DataGAme (class DataGame): Information about the game
            Player: Player number (for debug / print purposes)
        """
        CounterFound = 0
        for i in range(0, len(self.cards)):
            # Search for roi or reine of atout
            if ((self.cards[i].rank == 6) or (self.cards[i].rank == 7)) and (self.cards[i].suit == DataGame.atout):
                CounterFound += 1
        
        if CounterFound == 2: # Player has the stöckr
            self.stockr = True


    def RemoveCardsFromAnnonce (self, StartPos, FinalPos):
        """ Remove from the hand the cards used to calculate the annonce

        Args:
            Self (class Hand): copied hand of the player to check, or remaining after previous checks
            StartPos: Position of the first card of the annonce in the hand
            FinalPos: Position of the last card of the annonce in the hand
        """
        for i in range(StartPos, FinalPos+1):  
            self.add_card_annonce(self.pop_card(StartPos)) # Always use "StarPos" because each time we remove a card, all next ones are going one position less


    def Check4SameRank(self, DataGame, SearchedScore, player):
        """ Checks if a 4 of same rank (from 9 and above) exists. If found, remove the cards from the hand

        Args:
            Self (class Hand): copied hand of the player to check, or remaining after previous checks
            DataGAme (class DataGame): Information about the game
            SearchedScore: Level of annonce to be checked
            OriginalHand: Initial hand of the player (do not modify that hand)
            
        Output:
            * Found True if found
            
        Output is (when exists) a 4-cards with maximum annonce value. If several exist, the bigger rank based on rank_annonces is used
        """
        Found = False # Will be true if the searched anonce is found
        SuitFound = -1 # Will contain MaxRow if annonce found
        RankFound = -1 # Will contain rank. If several, priority to atout. Otherwise, don't care
        ScoreFound = 0 # Will containt the score of the best 4-cards set found
        CurrentMaxScore = 0 # Will contain maximum score found
        CounterCards = 0 # Will count how many cards are in a row
        PreviousRank, PreviousSuit = -1, -1 # Init with impossible values
        
        FakeCard = self.cards[0] # Just define a fake card to use this object later

        nb_removed_cards = 0 # Will contain the number of cards removed from the hand to correct the position
        # Ideally: Re-sort cards by Rank only. Create temporary hand for doing that. Cannot use copy because cards contains pictures
        self.sortbyrank() # The list is now sorted by rank only (temporarily)
        max = len(self.cards)
        for i_orig in range(0, max):
            # Correct the i_orig in case some cards were removed
            i = i_orig - nb_removed_cards
            # Check that Suite is same and range higher
            pcard = self.cards[i-1] # To simplify call on previous card studied
            card = self.cards[i] # To simplify call on current card studied
            if self.cards[i].rank == PreviousRank:
                # Card i is same rank that previous, need to update counter
                CounterCards = CounterCards + 1 # We have one card more in the row
                if CounterCards == 4: # We already found 4 cards of same rank
                    # Calculate score of cards found.
                    TmpScore = card.rank_annonces_points[card.rank_annonces.index(card.rank_names[card.rank])]
                    if TmpScore == SearchedScore: # This is the score we are looking for
                        self.annonces.append([SearchedScore, SearchedScore, card.rank])
                        print ("Annonce 4-cards same rank found for player " + str(player)+ " in rank " + str(FakeCard.rank_names[card.rank])) 
                        self.RemoveCardsFromAnnonce (i-CounterCards+1, i)
                        nb_removed_cards = nb_removed_cards + CounterCards # Store the number of removed card to correct the index
                        Found = True
                        
                    CounterCards = 0 # Reset counter
            else: # Just store the found rank
                    PreviousRank = card.rank
                    CounterCards = 1 # We have one card in the row

        print ("End of function Check4SameRank, result: ", str(Found))
        return Found


    def CheckCardsInarow(self, DataGame, SearchedScore, player):
        """ Checks if cards -in-a-row or exist, for the given announce value
        
        Args:
            Self (class Hand): copied hand of the player to check, or remaining after previous checks
            DataGAme (class DataGame): Information about the game
            SearchedScore: Level of annonce to be checked
            OriginalHand: Initial hand of the player (do not modify that hand
            
        Prerequisite: Cards in the hand ordered by suit and then rank
        """
        
        self.sort()  # First order by suit and rank (standard sorting)
        FakeCard = self.cards[0] # Just define a fake card to use this object later
        
        Found = False # Will be true if the searched anonce is found
        fRowSize = -1 # Will contain the length of the row found
        fSuit = -1 # Will contain the suit ID if annonce found
        fRank = -1 # Will contain rank. If several, priority to atout. Otherwise, don't care
        CounterCards = 0 # Will count how many cards are in a row
        PreviousRank, PreviousSuit = -1, -1 # Init with impossible values
        nb_removed_cards = 0 # Will contain the number of cards removed from the hand to correct the position
        max = len(self.cards)
        for i_orig in range(0, max):
            # Correct the i_orig in case some cards were removed
            i = i_orig - nb_removed_cards
            # Check that Suite is same and range higher by one
            if self.cards[i].suit == PreviousSuit and self.cards[i].rank == PreviousRank + 1:
                # Card i is part of a row, need to update counter
                CounterCards = CounterCards + 1 # We have one card more in the row
                PreviousSuit = self.cards[i].suit
                PreviousRank = self.cards[i].rank
            else:
                if (CounterCards >= 3): # No need to check anything if the row is below 3
                    # Check if the length of the row Corresponds to the searched score
                    if (CounterCards == 3 and SearchedScore == 20) or \
                        (CounterCards == 4 and SearchedScore == 50) or \
                            (CounterCards >= 5 and SearchedScore == 100):
                        if (self.cards[i-1].suit == DataGame.atout):
                            ComparisonPoints = SearchedScore + 1 # Add 1 to the comparison score for future sorting
                        else:
                            ComparisonPoints = SearchedScore # When it is not atout
                        self.annonces.append([ComparisonPoints, SearchedScore, self.cards[i-1].rank]) # Happen annonce to the list of the player
                        print ("Annonce in-a-row found for score " + str(SearchedScore) + " in rank " + str(FakeCard.rank_names[self.cards[i - 1].rank]) + " for player " + str(player)) 
                        self.RemoveCardsFromAnnonce (i-CounterCards, i-1) # Remove cards used for the annonce
                        nb_removed_cards = nb_removed_cards + CounterCards # Store the number of removed card to correct the index
                         
                # In all cases, at the end we store current suit and rank (new card for potential new suite)
                PreviousSuit = self.cards[i_orig - nb_removed_cards].suit # Using nb_removed_cards because we may have removed cards before in the same loop execution
                PreviousRank = self.cards[i_orig - nb_removed_cards].rank 
                CounterCards = 1 # Reset counter to 1 (we have 1 card in the suit)

        # We are just out of the for loop, maybe the current found row has to be counted
        if (CounterCards >= 3): # No need to check anything if the row is below 3
            # Check if the length of the row Corresponds to the searched score
            if (CounterCards == 3 and SearchedScore == 20) or \
                (CounterCards == 4 and SearchedScore == 50) or \
                    (CounterCards >= 5 and SearchedScore == 100):
                if (self.cards[i-1].suit == DataGame.atout):
                    ComparisonPoints = SearchedScore + 1 # Add 1 to the comparison score for future sorting
                else:
                    ComparisonPoints = SearchedScore # When it is not atout
                self.annonces.append([ComparisonPoints, SearchedScore, self.cards[i-1].rank]) # Happen annonce to the list of the player
                print ("Annonce in-a-row found for score " + str(SearchedScore) + " in rank " + str(FakeCard.rank_names[self.cards[i].rank]) + " for player " + str(player)) 
                self.RemoveCardsFromAnnonce (i-CounterCards+1, i) # Remove cards used for the annonce
        return

class HandSet(Hand):
    """Represents a list of players."""
    
    default_players_names = ["Coralie", "Alain",  "Nathaël", "Sandrine"]
    
    def __init__(self, label=''):
        self.players = []
        self.TeamAnnonce = -1 # Will contain -1 or the number of the team (0 or 1) which annonces should be counted

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

    def check_if_second_stockr(self, pos_card, DataGame, player):
        """ Checks, if the user had Stockr initially, if he is playing the second card
            
            Return: True if the player is currently playing the second stöckr card
        """
        if not self.players[player].stockr:
            return False # The player didn't have Stockr at the beginning

        # Check that we are playing a potential stockr card
        if not ((self.players[player].cards[pos_card].suit == DataGame.atout) and \
            (self.players[player].cards[pos_card].rank == 6) or (self.players[player].cards[pos_card].rank == 7)): # Rank 6 or 7: Reine or Roi.
            return False # Player is not currently playing a stockr card
        NbStockrCardsFound = 0
        for i in range(len(self.players[player].cards)):
            if ((self.players[player].cards[i].rank == 6) or \
                (self.players[player].cards[i].rank == 7)) and (self.players[player].cards[i].suit == DataGame.atout):
                NbStockrCardsFound += 1
        
        if NbStockrCardsFound == 1: # Only the card to be player has been found, so this is the second card to be played
            return True
        else:
            return False
        

    
    def action_play_card(self, pos_card, played_deck, TeamWonSet, DataGame, Scores):
        """ Get the card at pos_card from the player hand, and mot it to the played deck. Potentially also moves the cards to the TeamWonSet """
        
        # Before moving the card, check if we are in situation to add a stockr annonce
        if self.check_if_second_stockr(pos_card, DataGame, DataGame.current_player):
            # Add 20 points to the related team
            Scores.AddSetScore(DataGame.current_player % 2, 20)      

        # Then pop and add the card on the played deck
        myCard = self.players[DataGame.current_player].pop_card(pos_card)
        played_deck.add_card(myCard)
              
         
        played_deck.check_end_turn_and_move_cards(DataGame, TeamWonSet) # This function will change current player.

        # Do actions that are only necessary when playing standalone
        if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Standalone"):
            if DataGame.preferences.LockDisplay:
                DataGame.key_confirmed = False # Invalidate user

    def action_card_selected(self, player, pos_card, DataGame, played_deck, TeamWonSet, Scores):
        """ If found, select the atout or move card depending on game state, or send info to server

        Return: True if everything could be executed. False if for any reason is was not possible to execute the action

        Note: The return value is used mainly in server mode to say the call function that the action was refused
        """
        WasActionDone = False # Flag to know at the end if we could use the selected card and execute the action, or not.
        PlayerNumerAtStart = DataGame.current_player # Store the player at the begining because it may change further

        if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Client") and (DataGame.cli_connection.state != DataGame.cli_connection.CliStates.index("Master")):
            # The user clicked on a card, he is a client, but he is not the master, so ignore the clic action
            return False

        if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Client"):
            Con = DataGame.cli_connection
            Con.cli_send_card_selected(pos_card) # Send the selected card to server. Issue: I don't have the connection infos... to call the object
            Con.state = Con.CliStates.index("WaitServer") # Change state so that the client will then wait for server feed-back
            return True # Stop here: we did the job by informing the server
        else:
            if DataGame.is_this_game_state("Play"): # We are in play mode, so select atout or chibre
                if self.IsCardAllowedToBePlayed(player, pos_card, played_deck, DataGame): # Check that card is allowed in the context
                    self.action_play_card(pos_card, played_deck, TeamWonSet, DataGame, Scores)  # This function will change current player.
                    if DataGame.is_this_network_mode("Standalone") or DataGame.is_this_network_mode("Server"):
                        DataGame.ErrorState = DataGame.ErrorStates.index("NoError")
                        print ("Hand action_card_selected OK")
                        # Now either the new player is the server (So need to be master), or a client (need to go WaitClient)
                        if DataGame.is_this_network_mode("Server"):
                            if DataGame.current_player == 0: # This is the new player as it has been updated in action_play_card
                                DataGame.SrvComObject.srv_change_state("Master")
                            else:
                                DataGame.SrvComObject.srv_change_state("WaitClient")
                    WasActionDone = True
                else:
                    # If se are in standalone mode OR server mode, AND player 0, add some graphical effect to show that card is refused
                    if DataGame.is_this_network_mode("Standalone") or (DataGame.is_this_network_mode("Server") and DataGame.current_player == 0):
                        DataGame.ErrorState = DataGame.ErrorStates.index("NotAllowed")
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

                # The next function shows the full game for debug purpose. A breakpoint after this allows to take a picture of all cards
                # DataGame.debug_GameBoard.update_show_full_game(DataGame, DataGame.debug_handset, DataGame.debug_TeamWonSet, DataGame.scores, DataGame.card_picts, DataGame.PlayedDeckHand)
                
                if self.AnnoncesFullCheck(DataGame, DataGame.Scores): # Check if all users annonces, compare value and add points to the team if needed
                    DataGame.set_game_state("ShowAnnonces") # Change State to ShowAnnonces
                    if DataGame.is_this_network_mode("Server"):
                        DataGame.SrvComObject.srv_send_annonces(self) # Send the annonces to clients to allow them to display them
                        DataGame.SrvComObject.srv_send_force_state("ShowAnnonces")
                    # DataGame.SrvComObject.srv_send_all_data(self, DataGame, TeamWonSet, played_deck) # Send all data include new state and cards of annonce
                else:
                    DataGame.set_game_state("Play") # Change State to Play
        
        # If the action was done, we have to update the game state if we are the server: it means
        
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

    def GetPlayerWithBestAnnonce(self, DataGame):
        """ Compare tables of Annonce of each player to determine which one has the best annonce
        
        Args:
            Self (class Handset): copied hand of the player to check, or remaining after previous checks
            DataGAme (class DataGame): Information about the game
            
        Outputs:
            ID of the player when found
            -1 in case of no annonce
        """
        # Reminder; list content is: [ComparisonPoints, RealPoints, RefCard]
        FoundPlayer = -1 # Default initialization
        CurrentBestScore = 0 # Default initialization
        CurrentHigherCard = -1 # Default initialization

        for i in range (0,4): # Loop on the players.
            if len(self.players[i].annonces) >= 1: # Check that the list is not empty
                if self.players[i].annonces[0][0] > CurrentBestScore: # Check player i, position 0, corresponding to "RealPoints"
                    CurrentBestScore = self.players[i].annonces[0][0]  # Best score is always in first row
                    CurrentHigherCard = self.players[i].annonces[0][2] # The 2 corresponds to position "RefCard", so the rank of the card
                    FoundPlayer = i # Store the player
                elif self.players[i].annonces[0][0] == CurrentBestScore: # Same value. Then go to check higher card and place in turn
                    if (self.players[i].annonces[0][2] > CurrentHigherCard) or \
                        ((self.players[i].annonces[0][2] == CurrentHigherCard) and (i - DataGame.current_first_player_set < 0)): # TODO: Check that current_first_player_set is really set to the good value before Annonce checks
                        # If we reach that point, either the card is higher, or it is equal, but the player played before
                        CurrentBestScore = self.players[i].annonces[0][0] # Best score is always in first row
                        CurrentHigherCard = self.players[i].annonces[0][2] # The 2 corresponds to position "RefCard", so the rank of the card
                        FoundPlayer = i # Store the player
        
        return FoundPlayer
    
    def AddAnnouncesScores(self, LocalHandset, Scores, WinnerTeam):
        """ Add the scores found for WinnerTeam to the corresponding total Score
        
        Args:
            Self (class Handset): copied hand of the player to check, or remaining after previous checks
            Scores: Object on which to add annonces values
            WinnerTeam: The Team for which we have to count Annonces
        """
        PlayerToCount = WinnerTeam # 0 if team 0, 1 if team 1
        for i in range(0,2):
            PlayerToCount = WinnerTeam + 2*i # Define player to check
            for annonce in range (0, len(LocalHandset.players[PlayerToCount].annonces)):
                NewScoreToAdd = LocalHandset.players[PlayerToCount].annonces[annonce][1]
                Scores.AddSetScore(WinnerTeam, NewScoreToAdd)
        return

    def copy_annonces_cards(self, LocalHandset, Player):
        """ Copy the cards of found annonces in the real standard hands
        
        Args:
            Self (class Handset): Real Handset, in which the annonces cards must be copied
            LocalHandset: temporary object used for checking annonce, in which announce cards are located
            Player: Player of the passed hand
        """
        # Copy from LocalHandset.annonces_cards to self.annonces_cards
        self.players[Player].annonces_cards = copy.deepcopy(LocalHandset.players[Player].annonces_cards)
        return

    def AnnoncesFullCheck(self, DataGame, Scores):
        """ Check all annonces, defines the best one and add to the scores
        
        Args:
            Self (class Handset): handset of the players
            DataGame: Datas of the game
            Scores: Object on which to add annonces values

        Return: Returns true if at least one annonce is found and that we need to display them
        """
        # For each player
            # Copy hand ==> OK
            # Check each type of annonce in the following order, and remove cards from copied hand: ==> OK
                # Check 200 annonce
                # Check 150 annonce
                # Check 100 annonce: 4 identical (As, roi, reine, dame, dix)
                # Check 100 annonce: 5 or more in a row. Add 1 if atout. 
                # Check 50 annonce: 4 in a row. Add 1 if atout
                # Check 20 annonce: 3 in a row. Add 1 if atout
                # If annonce found, store in a table of the player the infos [ComparisonPoints, RealPoints, RefCArd]
        
        # Compare first lines of the 4 tables. The winner is the one with highest comparison points ==> OK
        # If equal, player first have priority ==> OK
        # This defines the team (0 or 1) ==> OK
        # Sum up all RealPoints for each player or the selected team and add to the score ==> ONGOING
        # Display score and list of cards with annonce

        # For each player
            # Check stöckr. Store info in data of player who has stöckr (except if already part of annonce)
            # In the course of the game, check when playing a card, if player had stockr, if it is the second one

        ValidAnnoncesFound = False # Will be true if annonces found (except if only stöckr)
        # Create temporary handset object for announce search purposes
        LocHandset = HandSet("tmp")
        # Copy each player hand
        for i in range (0,4): # TODO: Get game data and do loop based on number of players
            tmpHand = copy.deepcopy(self.players[i])
            LocHandset.add_Hand(tmpHand) # Add the copied hand to the handset
        
        # Check all kind of annonce, in the order of value
        for player in range (0,4): # Loop on the players. TODO: Use variable
            LocHandset.players[player].Check4SameRank(DataGame, 200, player) # Search for 200 annonce
            LocHandset.players[player].Check4SameRank(DataGame, 150, player) # Search for 150 annonce
            LocHandset.players[player].Check4SameRank(DataGame, 100, player) # Search for  100 annonce: 4 identical (As, roi, reine, dame, dix)
            LocHandset.players[player].CheckCardsInarow(DataGame, 100, player) # Check 100 annonce: 5 or more in a row. Add 1 if atout.
            LocHandset.players[player].CheckCardsInarow(DataGame, 50, player) # Check 50 annonce: 4 in a row. Add 1 if atout
            LocHandset.players[player].CheckCardsInarow(DataGame, 20, player) # Check 20 annonce: 3 in a row. Add 1 if atout

        BestPlayer = LocHandset.GetPlayerWithBestAnnonce(DataGame) # Get the player number with best Annonce. It can be -1 if no annonce found at all
        if (BestPlayer != -1): # Sanity check
            self.TeamAnnonce = BestPlayer % 2 # Define The Team Number on which we will count points
            self.AddAnnouncesScores(LocHandset, Scores, self.TeamAnnonce)
            ValidAnnoncesFound = True
        
        # Need now to check the Stöckr. As it could be the same cards than other annonce, we have to look in original full hands (so not LocHandset)
        for player in range (0,4):
            self.players[player].check_stockr(DataGame, player)

        if ValidAnnoncesFound:
            # Need to copy poped cards for the team with valid annonces from LocHandset to standard handset for future display
            self.copy_annonces_cards(LocHandset, self.TeamAnnonce) # First player of the team
            self.copy_annonces_cards(LocHandset, self.TeamAnnonce+2) # Second player of the team

        return ValidAnnoncesFound
