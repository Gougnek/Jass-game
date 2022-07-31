""" This file is part of a sample of the swiss Jass game implementation

    Classes in that file manage objects and methods related GameData
    GameData contains all information necessary during the game, with methods to update them
"""

from Preferences import Preferences

class GameData:
    """ Explanations for GamesStates
    "Init" is when the game is initializing the first time
    "SelAtout" is when the first play has to choose atout or chibre
    "SelAtoutChibre" is when the first user has chibred and we are waiting for the other player in the team to select atout
    "Play" is when the user has to select his card
    "Results" is when the set is finished,  but we are displaying set statistics (like scores)
    "Finished" is when the user validated the result State to go further
    """
    GameStates = ["Init", "SelAtout", "SelAtoutChibre", "Play", "Results", "Finished"]
    ErrorStates = ["NoError", "NotAllowed"]

    def __init__(self, NbPlayers):
        self.nbplayers = NbPlayers # Nb players in the game
        self.atout = -1 # Will contain later the reference on the atout
        self.state = self.GameStates.index("Init")
        self.latest_winner = -1 # Store the information of who won the latest turn (usage: defines who starts the new turn)
        self.current_player = -1 # Current player in turn
        self.current_turn_first_player = 0 # first player of the current turn (usage: link played cards to the player who played it)
        self.current_set = 1 # Defines in a game in which set we are (usage: just statistics)
        self.current_first_player_set = -1 # First player of the current set (usage: atout selection on next player at next set)
        self.preferences = Preferences() # Add a set of default preferences to GameData
        self.key_confirmed = False # Will store if current player confirmed by a key he is in front of the screen
        self.local_player_num = -1 # Only used by clients to store which player they really are
        self.cli_connection = -1 # For an easier access, will contain the reference to connection when in client mode
        self.game_board = None # Will contain a reference to the GameBoard object for an easier access
        self.SrvComObject = None # In case of run as server, will containt a ref. to the server connection object for an easier access
        self.Scores = None # Will be a pointer on the score object
        self.ErrorState = self.ErrorStates.index("NoError") # Contain last action status (error or not) to adapt background color

        # Link to other objects to allow full debug here
        self.debug_GameBoard = None
        self.debug_handset = None
        self.debug_TeamWonSet = None
        self.scores = None
        self.card_picts = None
        self.PlayedDeckHand = None

    def is_this_network_mode(self, network_mode):
        """ Check if the passed "network_mode" value against real mode 
        
        Return true if the passed network_mode is the current one.
        """
        return self.preferences.NetworkMode == self.preferences.NetworkModesList.index(network_mode)
    
    def is_this_game_state(self, game_state):
        """ Check if the passed "game_state" value against real state 
        
        Return true if the passed game_state is the current one.
        """
        return self.state == self.GameStates.index(game_state)
    
    def is_NOT_this_game_state(self, game_state):
        """ Check if the passed "game_state" value against real state 
        
        Return true if the passed game_state is the current one.
        """
        return self.preferences.NetworkMode != self.preferences.GameStates.index(game_state)
    
    def define_attout(self, atout_id):
        self.atout = atout_id # To define the attout
    
    def set_current_player(self, PlayerID):
        self.current_player = PlayerID
        print ("New Current player is " + str(PlayerID))

    def set_current_turn_first_player(self, PlayerID):
        self.current_turn_first_player = PlayerID

    def set_game_state(self, NewGameState):
        """ Changes the state of the game """
        if self.state != NewGameState:
            print ("Changing game state to " + NewGameState)
        self.state = self.GameStates.index(NewGameState)

    def UpdateIfSetFinished(self, handset, DataGame):
        """ Check if the game (current set) is finished, and modify state in that case
        """
        if DataGame.is_this_network_mode("Client"):
            return # Don't do anything if we are client

        finished = True
        for i in range (self.nbplayers):
            if len(handset.players[i].cards) > 0:
                finished = False
        if finished:
            # Do that only if we are not already back to Init, because finishing before starting doesn't make any sense
            if self.state == self.GameStates.index("Play"):
                self.set_game_state("Results") # Game is in finished state
    
    def SetNextPlayer(self):
        """ Set next player based on current one (select next one or go back to list start if this is the last one)
        """
        if (self.current_player >= self.nbplayers -1):
            self.current_player = 0
        else:
            self.current_player = self.current_player + 1  

    def SetNextTurnFirstPlayer(self):
        """ Set the turn first and current player to the latest winner
        """
        self.current_turn_first_player = self.current_player = self.latest_winner

    def Reset(self):
        """ Reset is called at the end of a set to prepare the next one
        """
        self.atout = -1 # Will contain later the reference on the atout
        self.latest_winner = -1 # Erase the information of who won the last deck
        self.current_turn_first_player = self.current_first_player_set + 1 % self.nbplayers # first player of the current turn
        self.current_first_player_set = self.current_turn_first_player
        self.current_player = self.current_turn_first_player # Current player in turn
        self.set_game_state("SelAtout") # First stage
    
    def DebugDisplayCards(self):
        """ Will display all cards on the screen wherever in the code for debug purposes"""


        