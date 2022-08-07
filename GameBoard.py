"""This file contains a sample of the swiss Jass game implementation

GameBoard.py i contains most of graphical functions of the program

    Distribution of this file is free of rights
"""

import pygame
from Card import CardsPictures, Card, CardPicture, Atout
from Deck import Deck
from pathlib import Path

class GameBoard:
    """Class containing all graphical functions."""
    
    def __init__(self, Height, Width):
        size = (Width, Height)
        self.screen = pygame.display.set_mode(size)

        self.ChibreColor = (180, 180, 180) # Color of the Chybre name
        self.ScoresColor = (200, 100, 90) # Color of the scores
        self.PlayerNumberColor = (250, 250, 250) # Color of text giving player number
        pygame.display.set_caption("Jass")
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font_big = pygame.font.SysFont('Comic Sans MS', 30)
        self.font_small = pygame.font.SysFont('Comic Sans MS', 15)
        self.HandxShift = 30 # x start position to show hands
        
        #Load the atout pictures
        self.atout_cards = Atout()
        
        # Define a rectangle to position the "Chybre" text and detect clicks on it
        self.ChibreRect = pygame.Rect(self.screen.get_width() - 200, 0, 200, 50) # (Left, top, width, height)
        # Define a rectangle to position the "Atout" detect clicks on it
        self.AtoutRect = pygame.Rect(self.screen.get_width() - 61, 1, 60, 60) # (Left, top, width, height)

        # Load background picture when error
        PictureFileName = 'table_background_red.png'
        try:
            self.background_pic_error = pygame.image.load(Path("Data/") / PictureFileName)
        except:
            mypath = "Data/" + PictureFileName
            print(mypath + " not found.")

        # Load background standard picture
        PictureFileName = 'table_background.png'
        try:
            self.background_pic = pygame.image.load(Path("Data/") / PictureFileName)
        except:
            mypath = "Data/" + PictureFileName
            print(mypath + " not found.")

        # Load background picture when player inactive
        PictureFileName = 'table_background_grayed.png'
        try:
            self.background_pic_inactive = pygame.image.load(Path("Data/") / PictureFileName)
        except:
            mypath = "Data/" + PictureFileName
            print(mypath + " not found.")

    def SpecialClicks(self, x, y, DataGame, gameDisplay):
        """ Check special clicks, not related to clicking on the cards. Possiblities are:
        
        * Selection of "Chibre"
        * Click on the atout at the end

        Returns True if the click could be interpreted. False otherwise
        """
        if (DataGame.state == DataGame.GameStates.index("SelAtout")):
            # Detect if click on the rectangle
            if self.ChibreRect.collidepoint((x,y)):
                # Change current player and game mode.
                DataGame.current_player = (DataGame.current_player + 2) % 4 # Define other player in team as current player
                DataGame.set_game_state("SelAtoutChibre")
                DataGame.key_confirmed = False # Invalidate user
                return True
        
        if (DataGame.state == DataGame.GameStates.index("Finished")):
            # Detect if click on the atout. This means, new set should start
            if self.AtoutRect.collidepoint((x,y)):
                DataGame.set_game_state("Init")
                return True
        return False
            

    def GetCardByClick(self, x, y, DataGame, handSet, gameDisplay):
        """Return the player number as well as card position in his deck.

        x: horizontal position of the click
        y: vertical position of the click
        
        Return Player and CardPos. If player = -1, this mean nothing should be considered.
        If Player = -2, this means the click is valid, but this is a function not related to a player
        """
        # assuming that we have only the current player cards displayed at tbe hottom

        # Assuming for the moment that line height is 135, and column width is 91 pixels
        
        if self.SpecialClicks(x, y, DataGame, gameDisplay): # Special clic interpreted, return invalid
            return -1, -1
        # Player id deprecated, but temporarily, return the current one if card found
        
        W = self.screen.get_width()
        H = self.screen.get_height()

        delta_x = x - W//2 + 410 # 410 is 4.5 times 91 pixels (rounded) 
        CardPos = delta_x // 91
        # Sanity check: if we click left to the first card
        if CardPos < 0:
            return -1, -1
        if y >= H - 136:
            Player = DataGame.current_player
            # Check if that player has that card
            if handSet.TestCardExist(handSet.players[Player], CardPos):
                return Player, CardPos
            else:
                Player = -1 # The player doesn't have this card. Invalidate the selection
        else:
            Player = -1
        return Player, CardPos
        
    def show_atout(self, DataGame, gameBoard):
        """Shows the selected atout on the screen if it exists
        If it doesn't exist, either show text "chibre" or nothing if chibre is already done"""
        # Get screens size tupple
        W = gameBoard.screen.get_width()
        x, y = W-60-1, 1 #Coordinate for atout picture
        x1, y1 = W-200, 20 # Coordinates for "Chibre" text
        
        # Display atout if exists
        if DataGame.atout >= 0 and DataGame.atout <= 3: #Atout has been defined
            self.screen.blit(self.atout_cards.cards[DataGame.atout].picture, (x,y))
        else:
            if DataGame.state == DataGame.GameStates.index("SelAtout"):
                # First player to select atout, so he can chibre. Show the button
                textsurface = self.font_big.render('CHIBRE', False, gameBoard.ChibreColor)
                self.screen.blit(textsurface, (gameBoard.ChibreRect.left, (gameBoard.ChibreRect.bottom - gameBoard.ChibreRect.bottom) // 2))
        # If we don't have atout and cannot chibre, don't display anyhting

    def show_player_numbers(self, handset, GameData):
        """ Display the player number. There are different situation
        * Standalone: Just display the current player
        * Server/Client: Display your player number and the one currently playing
        
        """
        H, W = self.screen.get_height(), self.screen.get_width()

        if (GameData.preferences.NetworkMode == GameData.preferences.NetworkModesList.index("Standalone")):
            # Display the current player on the left of the cards
            textsurface = self.font_big.render('Joueur ' + str(GameData.current_player + 1) , False, self.PlayerNumberColor)
            self.screen.blit(textsurface, (3, H - 88))
        else:
            # Display the current player on the left of the cards
            textsurface = self.font_big.render('Joueur ' + str(GameData.local_player_num + 1) , False, self.PlayerNumberColor)
            self.screen.blit(textsurface, (3, H - 88))
            # In the other cases, we have to add the "playing player" info as it may be different
            textsurface = self.font_small.render('En cours ' + str(GameData.current_player + 1) , False, self.PlayerNumberColor)
            self.screen.blit(textsurface, (3, H - 40))

    def show_final_scores(self, Scores):
        W, H = self.screen.get_width(), self.screen.get_height()
        for i in range(2): # Loop on the two teams scores
            CurScore, TotScore = Scores.Team[i]
            textsurface = self.font_small.render('Score équipe ' + str(i + 1) + ' : ' + str(CurScore) + '/' + str(TotScore), False, self.ScoresColor)
            self.screen.blit(textsurface, (W-190, H//2 - 30 + i*30))
        pygame.display.flip() # Update the window content

    def show_scores(self, Scores):
        W, H = self.screen.get_width(), self.screen.get_height()
        for i in range(2): # Loop on the two teams scores
            CurScore, TotScore = Scores.Team[i]
            textsurface = self.font_small.render(str(i + 1) + ' : ' + str(CurScore), False, self.ScoresColor)
            self.screen.blit(textsurface, (3, H//2 + i*30))
        pygame.display.flip() # Update the window content
    
    def show_valid_annonces(self, DataGame, handset, card_picts):
        """ Show the cards of the annonce(s)
        
        Input:
            DataGame: Data form the game
            handset: the set of hands were looking for cards of annonce
        
        """
        W, H = self.screen.get_width(), self.screen.get_height()
        # Display a rectangle for annonces
        pygame.draw.rect(self.screen,(0,70,40),(35,H//2-115,W-80,185))
        # Display a title
        textsurface = self.font_small.render("Annonces des joueurs de l'équipe " + str(handset.TeamAnnonce + 1), False, self.ScoresColor)
        self.screen.blit(textsurface, (45, H//2-115))
        # Display the cards
        x,y = 45, H//2-75
        for teams in range(2): # Loop on the two teams scores
            pl = teams*2 + handset.TeamAnnonce # Shortcut for the player for which to display annonces
            if len(handset.players[pl].annonces_cards) > 0: # Sanity check to avoid that list of annonces cards is empty
                x += teams*10 # Add 10 pixels before displaying annonces of the second player
                textsurface = self.font_small.render("Joueur " + str(pl + 1), False, self.ScoresColor)
                self.screen.blit(textsurface, (x, H//2-96))
                for CardPos in range(0,len(handset.players[pl].annonces_cards)):
                    self.screen.blit(card_picts.GetCardPicture(handset.players[pl].annonces_cards[CardPos].suit, handset.players[pl].annonces_cards[CardPos].rank), (x,y))
                    x=x+91

        pygame.display.flip() # Update the window content

    def update_backgroundPicture(self, DataGame):
        """ Fill the screen based on DataGame.ErrorState and DataGame. current_player """
        # If we are in error state, we should always put the error color
        if DataGame.ErrorState == DataGame.ErrorStates.index("NotAllowed"):
            self.screen.blit(self.background_pic_error, (0,0))
            return
        # No error. So either we are in turn, or not
        if DataGame.is_this_network_mode("Server"):
            if DataGame.current_player == 0: # We are server, check if we are player 0
                self.screen.blit(self.background_pic, (0,0))
            else:
                self.screen.blit(self.background_pic_inactive, (0,0))
            return
        elif DataGame.is_this_network_mode("Client"): # We are client
            if DataGame.current_player == DataGame.local_player_num: # We are server, check if we are player 0
                self.screen.blit(self.background_pic, (0,0))
            else:
                self.screen.blit(self.background_pic_inactive, (0,0))
            return
        #Default
        self.screen.blit(self.background_pic, (0,0))
        return

    def update_show_full_game(self, DataGame, handset, TeamWonSet, scores, card_picts, PlayedDeckHand):
        """ Debug function to show all cards on the screen"""
        self.update_backgroundPicture(DataGame)
        self.show_atout(DataGame, self) # Display the selected atout
        for i in range(DataGame.nbplayers):
            handset.players[i].show_cards_debug(self, i, card_picts)
        
        pygame.display.flip() # Update the window content
        self.clock.tick(10)
        return

    def update(self, DataGame, handset, TeamWonSet, scores, card_picts, PlayedDeckHand):
        # Special case: When we want to debug annonce, display all the game
        """ if DataGame.debug_annonce:
            self.update_show_full_game(DataGame, handset, TeamWonSet, scores, card_picts, PlayedDeckHand)
            pygame.display.flip() # Update the window content
            self.clock.tick(10)
            return """
        
        self.update_backgroundPicture(DataGame)

        PlayedDeckHand.show_played_cards(self.screen, card_picts)
        for i in range(2):
            TeamWonSet.players[i].show_won_cards(self, PlayedDeckHand, i, DataGame, card_picts)
        
        self.show_atout(DataGame, self) # Display the selected atout
        
        # Special case: If we need to display the annonces, just do that now and don't display the rest
        if DataGame.state == DataGame.GameStates.index("ShowAnnonces"): 
            self.show_valid_annonces(DataGame, handset, card_picts) # Show the annonces
            self.clock.tick(10)
            return

        self.show_player_numbers(handset, DataGame) # Show numbers of players
            

        for i in range(DataGame.nbplayers):
            # Case we are standalone:
            if DataGame.is_this_network_mode("Standalone"):
                if ((i == DataGame.current_player or DataGame.preferences.ShowAllCards) and ((not DataGame.preferences.LockDisplay) or (DataGame.preferences.LockDisplay and DataGame.key_confirmed))): # Display only cards from player it is the turn and if we are in "Play" status
                    if DataGame.preferences.ShowCardsFan:
                        handset.players[i].show_cards_fan(self, i, handset, card_picts)
                    else:
                        handset.players[i].show_cards(self, i, card_picts)
            else: # We are in either client or server mode. Need to take the local_player_num info into account. Only display if we are this player
                if i == DataGame.local_player_num:
                    if DataGame.preferences.ShowCardsFan:
                        handset.players[i].show_cards_fan(self, i, handset, card_picts)
                    else:
                        handset.players[i].show_cards(self, i, card_picts)
                

        if DataGame.state == DataGame.GameStates.index("Results"): # Game is in finished state): # Game is finished
            scores.CalculateScores(DataGame, TeamWonSet)
        if DataGame.state == DataGame.GameStates.index("Finished"):
            DataGame.game_board.show_final_scores(scores)
        else:
            DataGame.game_board.show_scores(scores) # Show current game scores (annonces + stöckr)


        pygame.display.flip() # Update the window content
        # This limits the while loop to a max of 60 times per second.
        # Leave this out and we will use all CPU we can.
        self.clock.tick(10)


