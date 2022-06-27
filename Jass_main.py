"""This file contains a sample of the swiss Jass game implementation

    Distribution of this file is free of rights
"""

from __future__ import print_function, division
# from asyncio.proactor_events import _ProactorBaseWritePipeTransport
from pathlib import Path
import math, random, pygame, copy, time
import socket, selectors, types, sys, pickle
from Preferences import Preferences
from GameData import GameData
from Deck import Deck
from Card import CardsPictures, Card, CardPicture, Atout
from Hand import Hand, HandSet
from GameBoard import *
import SrvCom, ClientCom
         
class GameBoardOld:
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
                DataGame.set_game_state("SelAtoutChibre")
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
            TeamWonSet.players[i].show_won_cards(self, deck, i, DataGame, card_picts)
        
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
            ScreenGame.show_scores(scores)


        pygame.display.flip() # Update the window content
        # This limits the while loop to a max of 60 times per second.
        # Leave this out and we will use all CPU we can.
        self.clock.tick(10)

class Scores:
    """ Class containing current set of scores as well as full game scores."""
    ScoresTypes = ["Set", "Game"]
    def __init__(self, NbTeams):
        self.Team = []
        for i in range(NbTeams):
            self.Team.append((0,0)) # Append Set, Game score with value 0
    
    def CalculateScores(self, DataGame , SetTeamWon):
        """ Calculate the score for each team

        Missing: assumes here only 2 teams. Not compatible for parties <> than 4 players
        """
        # Don't do anything if we are not in "Result" state
        if DataGame.state != DataGame.GameStates.index("Results"):
            return

        for TeamSetID in range(2):
            Score = PreviousScore = 0
            # Check special case: In case the team has ALL cards
            if len(SetTeamWon.players[TeamSetID].cards) == 36:
                Score = 257
            else:
                for i in range(len(SetTeamWon.players[TeamSetID].cards)):
                    PreviousScore = Score
                    CurCard = SetTeamWon.players[TeamSetID].cards[i] # Shorter object name for convenience
                    CurSuite = SetTeamWon.players[TeamSetID].cards[i].suit
                    if CurSuite == DataGame.atout:
                        Score += CurCard.rank_points_atout[CurCard.rank]
                    else:
                        Score += CurCard.rank_points[CurCard.rank]
                # Check if this team wons the ending 5 points
                if DataGame.latest_winner % 2 == TeamSetID: # Module 2 the winner number to find team number
                    Score += 5
           
            # Store the total
            self.Team[TeamSetID] = Score, self.Team[TeamSetID][1] + Score # Store current score and add to game score
        
        # Change Game stage to Finished
        DataGame.set_game_state("Finished")
        return

def ManageInterfaceEvents(DataGame, handset, TeamWonSet, PlayedDeckHand):
    """ Get user events and call related functions to execute the action
    
    Returns always false, except if the actions is to quit the game
    """
    Quit = False
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            Quit = True  # Flag that we are done so we exit this loop
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            player, pos_card = DataGame.game_board.GetCardByClick(x, y, DataGame, handset, ScreenGame)
            if player == -1: # Sanity check if the use clics on something valid
                continue # Stop here and go back to the top of the loop
            # If Sandalone or server: do the action on the card (can be selection of atout or playing it)
            handset.action_card_selected(player, pos_card, DataGame, PlayedDeckHand, DataGame.game_board, TeamWonSet)
            # Make it simple: if we are server, always request clients to update when there was a user clic.
            if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Server"):     
                DataGame.SrvComObject.srv_send_all_data(handset, DataGame, TeamWonSet, PlayedDeckHand)         
                
        if event.type == pygame.KEYDOWN:
            # Add Magic key for debug purposes (d = debug = 100)
            if (event.key == 100): # 'D' key, to debut
                None
            if (event.key == 112): # 'P' key, to call preference window
                DataGame.preferences.DisplayPrefWindow()
            handset.players[DataGame.current_player].CheckPlayerKey(pygame.key.name(event.key), DataGame)
    
    return Quit


def find_defining_class(obj, method_name):
    """Finds and returns the class object that will provide 
    the definition of method_name (as a string) if it is
    invoked on obj.

    obj: any python object
    method_name: string method name
    """
    for ty in type(obj).mro():
        if method_name in ty.__dict__:
            return ty
    return None


if __name__ == '__main__':
    # Check arguments passed. For the moment, assume only the mode exist
    ArgMode = ""
    if len(sys.argv) > 1:
        ArgMode = sys.argv[1]
        print ('Requested mode:', str(ArgMode))
        
    
    """ INIT PART """
    DataGame = GameData(NbPlayers = 4) # Create data game for 4 players
    
    # Override preferences if args passed at launch
    if ArgMode == "server": 
        DataGame.preferences.NetworkMode = DataGame.preferences.NetworkModesList.index("Server")
    elif ArgMode == "client":
        DataGame.preferences.NetworkMode = DataGame.preferences.NetworkModesList.index("Client")
    elif ArgMode == "standalone":
        DataGame.preferences.NetworkMode = DataGame.preferences.NetworkModesList.index("Standalone")

    # Check if we need to display the preference window at launch
    if DataGame.preferences.ShowPrefWindowAtStart:
        DataGame.preferences.DisplayPrefWindow()

    """ INITIALIZATION FOR ALL MODES """
    deck = Deck() # Create initial cards
    card_picts = CardsPictures() # Create object with all cards pictures (for and back grounds)
    deck.shuffle() # Shuffle the initial cards
    handset = HandSet() # Create a set of hands

    for i in range(DataGame.nbplayers):
        handset.add_Hand(Hand(i)) # Create each "Hand" and add it to the handset

    PlayedDeckHand = Hand("played") # Create a hand for the played card

    TeamWonSet = HandSet()  # Create a set of hands for won cards
    TeamWonSet.add_Hand(Hand(0)) # 0 is for team 1 (player 1&3)
    TeamWonSet.add_Hand(Hand(1)) # 1 is for team 2 (player 2&4)

    # Give name to each player
    handset.InitializePlayerNames(DataGame)

    # Create storage for scores
    scores = Scores(2)

    """ GAME INITIAL SETUP IF SERVER OR STANDALONE """
    # The following actions are not needed if we are client mode (data will be provided by the server)
    if DataGame.preferences.NetworkMode != DataGame.preferences.NetworkModesList.index("Client"):
        # Distribute the cards, set first player and change state
        deck.distribute_cards(handset, DataGame)
        handset.Inital_game_first_player(DataGame)
        DataGame.set_game_state("SelAtout") # Change initial state to "SelAtout"
    
    """ GRAPHICAL INIT PART """
    # Construct an object to display
    # ScreenGame = GameBoard( Width = 900, Height = 1200)
    ScreenGame = GameBoard(Height = 648, Width = 1152)
    DataGame.game_board = ScreenGame # Store reference to screen game for easier acess in functions
      
    """ SERVER INITIAL SETUP """
    if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Server"):
        mySrvComToClient = SrvCom.SrvCom() # Create an empty list with future clients connections
        DataGame.local_player_num = 0 # Define the server as the player 0
        mySrvComToClient.server_wait_all_players(3) # Wait tor all connections and store them in a table
        mySrvComToClient.srv_send_welcome_infos(DataGame) # Send initial welcome message
        mySrvComToClient.srv_send_all_data(handset, DataGame, TeamWonSet, PlayedDeckHand) # Send all data to all connected clients
        DataGame.SrvComObject = mySrvComToClient # Keep pointer to connection object for easier reference
        # Adapt mode based on first player (define by the call to Initial_game_first_player which should have been done before)
        if DataGame.current_player == 0: # Server is player 0 
            mySrvComToClient.srv_change_state("Master")  # Set state Master 
        else:
            mySrvComToClient.srv_change_state("WaitClient")  # Set state Client 
        pygame.display.set_caption("Jass server")
    
    """ CLIENT INITIAL SETUP """
    if DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Client"):
        # client_connect_and_test(handset) # Temporary: get the player 0 hand and returns
        myClientSocket = ClientCom.ClientSocket()
        myClientSocket.client_connect_to_server() # Crate connection to server and get the related socket
        # Store the reference of the Client Socket in GameData for an easier access
        DataGame.cli_connection = myClientSocket
        # Call a function that will listend and interpret initial commands
        myClientSocket.ListenAndInterpretCommands(PlayedDeckHand, TeamWonSet, handset, DataGame)
        pygame.display.set_caption("Jass client " + str(DataGame.local_player_num))
        print ("Client player number: " + str(DataGame.local_player_num))
    
    Quit = False
    
    """ EVENTS LOOP """
    while not Quit:
        """ CALL FUNCTIONS TO WAIT COMMUNICATION WHEN NOT STANDALONE """
        # Manage netowrk operation when CLIENT
        if (DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Client")):
            if myClientSocket.state == myClientSocket.CliStates.index("WaitServer"): # Only wait on network is the state is to wait
                # Stop the event loop and wait for receiving messages from the server
                myClientSocket.ListenAndInterpretCommands(PlayedDeckHand, TeamWonSet, handset, DataGame)
                Quit = False # To be removed
                None # Client is freed from waiting command (ready for update)

        # Manage network operation when SERVER
        if (DataGame.preferences.NetworkMode == DataGame.preferences.NetworkModesList.index("Server")):
            if mySrvComToClient.SrvState == mySrvComToClient.SrvStates.index("WaitClient"): # The server is supposed to wait on message from the client
                mySrvComToClient.srv_give_master_and_listen_commands(handset, PlayedDeckHand, TeamWonSet, DataGame) # Wait for action 
            # Verify who is in the turn: Client or server ? Adapt consequently
            if DataGame.current_player == 0: # By default, server is always player 0
                if mySrvComToClient.SrvState != mySrvComToClient.SrvStates.index("Master"):
                    mySrvComToClient.srv_change_state("Master")  # Set state Master  
            else: # Server is not the current player
                # Send YourTurn to client in charge and wait for message
                mySrvComToClient.srv_give_master_and_listen_commands(handset, PlayedDeckHand, TeamWonSet, DataGame) # Wait for action 
                # mySrvComToClient.srv_change_state("WaitClient")  # Set state waiting client    
                # mySrvComToClient.SrvState = mySrvComToClient.SrvStates.index("WaitClient")                    
        
        """ MANAGE USER ACTIONS """
        # The next function manages for any state all keyboard and mouse events that can happen. Returns true if quit option has been chosen
        Quit = ManageInterfaceEvents(DataGame, handset, TeamWonSet, PlayedDeckHand)

        """ PERFORM DATA UPDATE AND CALL GRAPHICAL UPDATE """
        # First define background color based on current state ==> Probably deprecated TODO
        if DataGame.ErrorState != DataGame.ErrorStates.index("NotAllowed"):
            DataGame.game_board.BackgroundColor = DataGame.game_board.BackgroundColorYourTurn
        # Update infos on handset and state if game is finished
        DataGame.UpdateIfSetFinished(handset)

        # Check if new game is requested after finished one (state changed)
        if DataGame.state == DataGame.GameStates.index("Init"):
            deck.ResetForNextSet(DataGame, handset, TeamWonSet)

        # Update the screen
        ScreenGame.update(DataGame, handset, TeamWonSet, scores, card_picts, PlayedDeckHand)

    # Be IDLE friendly
    # pygame.quit()
    
