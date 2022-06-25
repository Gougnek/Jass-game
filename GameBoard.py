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

        # self.Color = (0, 80, 0) # Dark Green by default
        self.BackgroundColor = (0, 80, 0) # This is the variable which will contain current background color to display at next refresh
        self.BackgroundColorOk = (0, 80, 0) # Dark Green
        self.BackgroundColorYourTurn = (0, 40, 0) # Very Dark Green. Usefull only in client-server mode
        self.BackgroundColorError = (100, 0, 0) # Dark Red when error occus
        self.ChibreColor = (180, 180, 180) # Color of the Chybre name
        self.ScoresColor = (200, 100, 90) # Color of the scores
        self.PlayerNumberColor = (0, 0, 0) # Color of the Player numbers
        self.PlayerNumberCurrentColor = (250, 250, 250) # Color of player in turn
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

        # Load background picture
        PictureFileName = 'table_background.png'
        try:
            self.background_pic = pygame.image.load(Path("Pictures/") / PictureFileName)
        except:
            mypath = "Pictures/" + PictureFileName
            print(mypath + " not found.")

    def SpecialClicks(self, x, y, DataGame, gameDisplay):
        """ Check special clicks, not related to clicking on the cards. Possiblities are:
        
        * Selection of "Chibre"
        * Click on the atout at the end
        """
        if (DataGame.state == DataGame.GameStates.index("SelAtout")):
            # Detect if click on the rectangle
            if self.ChibreRect.collidepoint((x,y)):
                # Change current player and game mode.
                DataGame.current_player = (DataGame.current_player + 2) % 4 # Define other player in team as current player
                DataGame.state = DataGame.GameStates.index("SelAtoutChibre")
                DataGame.key_confirmed = False # Invalidate user
        
        if (DataGame.state == DataGame.GameStates.index("Finished")):
            # Detect if click on the atout. This means, new set should start
            if self.AtoutRect.collidepoint((x,y)):
                DataGame.state = DataGame.GameStates.index("Init")

            

    def GetCardByClick(self, x, y, DataGame, handSet, gameDisplay):
        """Return the player number as well as card position in his deck.

        x: horizontal position of the click
        y: vertical position of the click
        
        Return Player and CardPos. If player = -1, this mean nothing should be considered.
        If Player = -2, this means the click is valid, but this is a function not related to a player
        """
        # assuming that we have only the current player cards displayed at tbe hottom

        # Assuming for the moment that line height is 135, and column width is 91 pixels
        
        self.SpecialClicks(x, y, DataGame, gameDisplay)
        # Player id deprecated, but temporarily, return the current one if card found
        
        W = self.screen.get_width()
        H = self.screen.get_height()

        delta_x = x - W//2 + 410 # 410 is 4.5 times 91 pixels (rounded) 
        CardPos = delta_x // 91
        if y >= H - 136:
            Player = DataGame.current_player
            # Check if that player has that card
            if handSet.TestCardExist(handSet.players[Player], CardPos):
                return Player, CardPos
        else:
            Player = -1
        return Player, CardPos
        
        """ 
        x,y = 1152//2 - 410, 648 - 136

        
        
        Player = y // 135
        CardPos = (x - gameDisplay.HandxShift) // 91
        # Check Speical Clicks
        if handSet.TestCardExist(handSet.players[Player], CardPos):
        
        # Check if player exists
        if Player < 0 or Player >= len(handSet.players):
            return -1, -1 # Player doesn't exist
        # Check that found player is the current player
        if Player != DataGame.current_player:
            return -1, -1 # It is not the turn of that player
        # Check if that player has that card
        if handSet.TestCardExist(handSet.players[Player], CardPos):
            return Player, CardPos
        else:
            return -1, -1 # Card doesn't exist """
        
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
        """ Show players numbers on the left, current player in RED"""
        for i in range(len(handset.players)):
            Color = self.PlayerNumberColor # Standard color
            if GameData.current_player == i: # Special color for current player
                Color = self.PlayerNumberCurrentColor # Override by in-turn color
            textsurface = self.font_big.render(str(i + 1) , False, Color)
            self.screen.blit(textsurface, (3, 135 // 2 - 25 + i*135))

    def show_scores(self, Scores):
        W, H = self.screen.get_width(), self.screen.get_height()
        for i in range(2): # Loop on the two teams scores
            CurScore, TotScore = Scores.Team[i]
            textsurface = self.font_small.render('Score équipe ' + str(i + 1) + ' : ' + str(CurScore) + '/' + str(TotScore), False, self.ScoresColor)
            self.screen.blit(textsurface, (W-190, H//2 - 30 + i*30))
        pygame.display.flip() # Update the window content

    def show_scores1(self, Scores):
        for i in range(2): # Loop on the two teams scores
            CurScore, TotScore = Scores.Team[i]
            textsurface = self.font_small.render('Score équipe ' + str(i + 1) + ' : ' + str(CurScore) + '/' + str(TotScore), False, self.ScoresColor)
            self.screen.blit(textsurface, (10, 700 + i*30))
        pygame.display.flip() # Update the window content



    def update_backgroundColor(self, DataGame):
        """ Fill the screen based on DataGame.ErrorState and DataGame. current_player """
        # If we are in error state, we should always put the error color
        if DataGame.ErrorState == DataGame.ErrorStates.index("NotAllowed"):
            self.screen.fill(self.BackgroundColorError)
            # print ("Player num ", DataGame.local_player_num, " or unique player color set to Error")
            return
        # No error. So either we are in turn, or not
        if (DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Server")):
            if DataGame.current_player == 0: # We are server, check if we are player 0
                self.screen.fill(self.BackgroundColorYourTurn)
                # print ("Player num ", DataGame.local_player_num, " color set to YourTurn as server")
                return
        elif (DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Client")): # We are client
            if DataGame.current_player == DataGame.local_player_num: # We are server, check if we are player 0
                # print ("Player num ", DataGame.local_player_num, " color set to YourTurn as client")
                self.screen.fill(self.BackgroundColorYourTurn)
                return
        #Default
        # print ("Player num ", DataGame.local_player_num, " color set as OK")
        self.screen.fill(self.BackgroundColorOk)
        return

    def update(self, DataGame, handset, TeamWonSet, scores, card_picts, PlayedDeckHand):
        # Test for debug purposes
        # self.update_backgroundColor(DataGame)
        self.screen.blit(self.background_pic, (0,0))

        PlayedDeckHand.show_played_cards(self.screen, card_picts)
        for i in range(2):
            TeamWonSet.players[i].show_won_cards(self, PlayedDeckHand, i, DataGame, card_picts)
        
        self.show_atout(DataGame, self) # Display the selected atout
        
        self.show_player_numbers(handset, DataGame) # Show numbers of players

        for i in range(DataGame.nbplayers):
            # Case we are standalone:
            if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Standalone"):
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
            DataGame.game_board.show_scores(scores)


        pygame.display.flip() # Update the window content
        # This limits the while loop to a max of 60 times per second.
        # Leave this out and we will use all CPU we can.
        self.clock.tick(10)


class GameBoard1:
    """Class containing all graphical functions."""
    
    def __init__(self, Height, Width):
        size = (Height, Width)
        self.screen = pygame.display.set_mode(size)

        # self.Color = (0, 80, 0) # Dark Green by default
        self.BackgroundColor = (0, 80, 0) # This is the variable which will contain current background color to display at next refresh
        self.BackgroundColorOk = (0, 80, 0) # Dark Green
        self.BackgroundColorYourTurn = (0, 40, 0) # Very Dark Green. Usefull only in client-server mode
        self.BackgroundColorError = (100, 0, 0) # Dark Red when error occus
        self.ChibreColor = (180, 180, 180) # Color of the Chybre name
        self.ScoresColor = (200, 100, 90) # Color of the scores
        self.PlayerNumberColor = (0, 0, 0) # Color of the Player numbers
        self.PlayerNumberCurrentColor = (250, 250, 250) # Color of player in turn
        pygame.display.set_caption("Jass")
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.HandxShift = 30 # x start position to show hands
        
        #Load the atout pictures
        self.atout_cards = Atout()
        
        # Define a rectangle to position the "Chybre" text and detect clicks on it
        self.ChibreRect = pygame.Rect(self.screen.get_width() - 200, 0, 200, 50) # (Left, top, width, height)
        # Define a rectangle to position the "Atout" detect clicks on it
        self.AtoutRect = pygame.Rect(self.screen.get_width() - 61, 1, 60, 60) # (Left, top, width, height)

    def SpecialClicks(self, x, y, DataGame, gameDisplay):
        """ Check special clicks, not related to clicking on the cards. Possiblities are:
        
        * Selection of "Chibre"
        * Click on the atout at the end
        """
        if (DataGame.state == DataGame.GameStates.index("SelAtout")):
            # Detect if click on the rectangle
            if self.ChibreRect.collidepoint((x,y)):
                # Change current player and game mode.
                DataGame.current_player = (DataGame.current_player + 2) % 4 # Define other player in team as current player
                DataGame.state = DataGame.GameStates.index("SelAtoutChibre")
                DataGame.key_confirmed = False # Invalidate user
        
        if (DataGame.state == DataGame.GameStates.index("Finished")):
            # Detect if click on the atout. This means, new set should start
            if self.AtoutRect.collidepoint((x,y)):
                DataGame.state = DataGame.GameStates.index("Init")

            

    def GetCardByClick(self, x, y, DataGame, handSet, gameDisplay):
        """Return the player number as well as card position in his deck.

        x: horizontal position of the click
        y: vertical position of the click
        
        Return Player and CardPos. If player = -1, this mean nothing should be considered.
        If Player = -2, this means the click is valid, but this is a function not related to a player
        """
        # Assuming for the moment that line height is 135, and column width is 51 pixels
        Player = y // 135
        CardPos = (x - gameDisplay.HandxShift) // 91
        # Check Speical Clicks
        self.SpecialClicks(x, y, DataGame, gameDisplay)
        
        # Check if player exists
        if Player < 0 or Player >= len(handSet.players):
            return -1, -1 # Player doesn't exist
        # Check that found player is the current player
        if Player != DataGame.current_player:
            return -1, -1 # It is not the turn of that player
        # Check if that player has that card
        if handSet.TestCardExist(handSet.players[Player], CardPos):
            return Player, CardPos
        else:
            return -1, -1 # Card doesn't exist
        
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
                textsurface = self.font.render('CHIBRE', False, gameBoard.ChibreColor)
                self.screen.blit(textsurface, (gameBoard.ChibreRect.left, (gameBoard.ChibreRect.bottom - gameBoard.ChibreRect.bottom) // 2))
        # If we don't have atout and cannot chibre, don't display anyhting

    def show_player_numbers(self, handset, GameData):
        """ Show players numbers on the left, current player in RED"""
        for i in range(len(handset.players)):
            Color = self.PlayerNumberColor # Standard color
            if GameData.current_player == i: # Special color for current player
                Color = self.PlayerNumberCurrentColor # Override by in-turn color
            textsurface = self.font.render(str(i + 1) , False, Color)
            self.screen.blit(textsurface, (3, 135 // 2 - 25 + i*135))

    def show_scores(self, Scores):
        for i in range(2): # Loop on the two teams scores
            CurScore, TotScore = Scores.Team[i]
            textsurface = self.font.render('Score équipe ' + str(i + 1) + ' : ' + str(CurScore) + '/' + str(TotScore), False, self.ScoresColor)
            self.screen.blit(textsurface, (10, 700 + i*30))
        pygame.display.flip() # Update the window content

    def update_backgroundColor(self, DataGame):
        """ Fill the screen based on DataGame.ErrorState and DataGame. current_player """
        # If we are in error state, we should always put the error color
        if DataGame.ErrorState == DataGame.ErrorStates.index("NotAllowed"):
            self.screen.fill(self.BackgroundColorError)
            # print ("Player num ", DataGame.local_player_num, " or unique player color set to Error")
            return
        # No error. So either we are in turn, or not
        if (DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Server")):
            if DataGame.current_player == 0: # We are server, check if we are player 0
                self.screen.fill(self.BackgroundColorYourTurn)
                # print ("Player num ", DataGame.local_player_num, " color set to YourTurn as server")
                return
        elif (DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Client")): # We are client
            if DataGame.current_player == DataGame.local_player_num: # We are server, check if we are player 0
                # print ("Player num ", DataGame.local_player_num, " color set to YourTurn as client")
                self.screen.fill(self.BackgroundColorYourTurn)
                return
        #Default
        # print ("Player num ", DataGame.local_player_num, " color set as OK")
        self.screen.fill(self.BackgroundColorOk)
        return

    def update(self, DataGame, handset, TeamWonSet, scores, card_picts, PlayedDeckHand):
        # Test for debug purposes
        self.update_backgroundColor(DataGame)
        PlayedDeckHand.show_played_cards(self.screen, card_picts)
        for i in range(2):
            TeamWonSet.players[i].show_won_cards(self, PlayedDeckHand, i, DataGame, card_picts)
        
        self.show_atout(DataGame, self) # Display the selected atout
        
        self.show_player_numbers(handset, DataGame) # Show numbers of players

        for i in range(DataGame.nbplayers):
            # Case we are standalone:
            if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Standalone"):
                if ((i == DataGame.current_player or DataGame.preferences.ShowAllCards) and ((not DataGame.preferences.LockDisplay) or (DataGame.preferences.LockDisplay and DataGame.key_confirmed))): # Display only cards from player it is the turn and if we are in "Play" status
                    handset.players[i].show_cards(self, i, card_picts)
            else: # We are in either client or server mode. Need to take the local_player_num info into account. Only display if we are this player
                if i == DataGame.local_player_num:
                    handset.players[i].show_cards(self, i, card_picts)
                

        if DataGame.state == DataGame.GameStates.index("Results"): # Game is in finished state): # Game is finished
            scores.CalculateScores(DataGame, TeamWonSet)
        if DataGame.state == DataGame.GameStates.index("Finished"):
            DataGame.game_board.show_scores(scores)


        pygame.display.flip() # Update the window content
        # This limits the while loop to a max of 60 times per second.
        # Leave this out and we will use all CPU we can.
        self.clock.tick(10)