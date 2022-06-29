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
            handset.action_card_selected(player, pos_card, DataGame, PlayedDeckHand, TeamWonSet)
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
    if DataGame.is_this_network_mode("Server") or DataGame.is_this_network_mode("Standalone"):
        # Distribute the cards, set first player and change state
        deck.distribute_cards(handset, DataGame)
        handset.Inital_game_first_player(DataGame)
        DataGame.set_game_state("SelAtout") # Change initial state to "SelAtout"
    
    """ GRAPHICAL INIT PART """
    # Construct an object to display
    ScreenGame = GameBoard(Height = 648, Width = 1152)
    DataGame.game_board = ScreenGame # Store reference to screen game for easier acess in functions
      
    """ SERVER INITIAL SETUP """
    if DataGame.is_this_network_mode("Server"):
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
        # The server must force first update, otherwise nothing will be visible
        ScreenGame.update(DataGame, handset, TeamWonSet, scores, card_picts, PlayedDeckHand)
        
    
    """ CLIENT INITIAL SETUP """
    if DataGame.is_this_network_mode("Client"):
        # client_connect_and_test(handset) # Temporary: get the player 0 hand and returns
        myClientSocket = ClientCom.ClientSocket()
        myClientSocket.client_connect_to_server() # Crate connection to server and get the related socket
        # Store the reference of the Client Socket in GameData for an easier access
        DataGame.cli_connection = myClientSocket
        # Call a function that will listend and interpret initial commands
        myClientSocket.ListenAndInterpretCommands(PlayedDeckHand, TeamWonSet, handset, DataGame)
        pygame.display.set_caption("Jass client " + str(DataGame.local_player_num))
        print ("Client player number: " + str(DataGame.local_player_num))
        DataGame.set_game_state("Play") # Change initial state to "Play" to avoid any issue. This will be overrided by infos sent by the server
    
    Quit = False
    
    """ EVENTS LOOP """
    while not Quit:
        """ CALL FUNCTIONS TO WAIT COMMUNICATION WHEN NOT STANDALONE """
        # Manage netowrk operation when CLIENT
        if DataGame.is_this_network_mode("Client"):
            if myClientSocket.state == myClientSocket.CliStates.index("WaitServer"): # Only wait on network is the state is to wait
                # Stop the event loop and wait for receiving messages from the server
                myClientSocket.ListenAndInterpretCommands(PlayedDeckHand, TeamWonSet, handset, DataGame)
                None # Client is freed from waiting command (ready for update)

        # Manage network operation when SERVER
        if DataGame.is_this_network_mode("Server"):
            if mySrvComToClient.SrvState == mySrvComToClient.SrvStates.index("WaitClient"): # The server is supposed to wait on message from the client
                mySrvComToClient.srv_give_master_and_listen_commands(handset, PlayedDeckHand, TeamWonSet, DataGame) # Wait for action 
            # Verify who is in the turn: Client or server ? Adapt consequently
            if DataGame.current_player == 0: # By default, server is always player 0
                if mySrvComToClient.SrvState != mySrvComToClient.SrvStates.index("Master"):
                    mySrvComToClient.srv_change_state("Master")  # Set state Master  
            # else: # Server is not the current player
                # Send YourTurn to client in charge and wait for message
            #    mySrvComToClient.srv_give_master_and_listen_commands(handset, PlayedDeckHand, TeamWonSet, DataGame) # Wait for action 
                 
        
        """ MANAGE USER ACTIONS """
        # The next function manages for any state all keyboard and mouse events that can happen. Returns true if quit option has been chosen
        Quit = ManageInterfaceEvents(DataGame, handset, TeamWonSet, PlayedDeckHand)

        """ PERFORM DATA UPDATE AND CALL GRAPHICAL UPDATE """
        # Update infos on handset and state if game is finished
        DataGame.UpdateIfSetFinished(handset, DataGame)

        # Check if new game is requested after finished one (state changed)
        if DataGame.is_this_game_state("Init"):
            deck.ResetForNextSet(DataGame, handset, TeamWonSet)

        # Update the screen
        ScreenGame.update(DataGame, handset, TeamWonSet, scores, card_picts, PlayedDeckHand)
        
    
