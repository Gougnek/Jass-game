""" This file is part of a sample of the swiss Jass game implementation

    Classes in that file manage all socket and connection related tasks for a client
"""

import socket, selectors, types, sys, pickle
import time, copy
import Hand
from SrvCom import DataGameToSend

class ClientSocket:

    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server 
    
    SrvMesHead = {"Welcome" : "WE", "PlayedCards": "PC", "WonCards" : "WC", "Hand": "HA", "GameData" : "GD", "YourTurn" : "YT", "CardValid" : "CV", "CardInvalid" : "CI", "Refresh" : "RE", "Scores" : "SC"} # From Server Messages types (Str) and headers (2 chars)
    CliStates = ["Init", "Master", "WaitServer"] # Possible states of the client mode
    CliMesHead = {"CardSelected" : "CS"} 

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock  
        self.state = self.CliStates.index("Init")
    
    def cli_change_state(self, NewState):
        if self.state != self.CliStates.index(NewState):
            print("Client becomes", NewState)
        self.state = self.CliStates.index(NewState)
        

    def client_connect_to_server(self):
        """ Create connection to the server """
        self.sock.connect((self.HOST, self.PORT))
    
    def client_update_gamedata(self, payload, GameData):
        """ Receive GameData from server (payload) and replace local game data
        """
        # Undump (result will be a object of identical type than the one sent)
        NewGameDataSubset = pickle.loads(payload)
        # Copy received data to game data
        GameData.atout = NewGameDataSubset.atout
        GameData.current_player = NewGameDataSubset.current_player
        GameData.nbplayers = NewGameDataSubset.nbplayers
        GameData.latest_winner = NewGameDataSubset.latest_winner
        return
    
    def client_welcome_infos(self, payload, GameData):
        WelcomeInfos = pickle.loads(payload)
        GameData.local_player_num = WelcomeInfos.PlayerNumber
        return
    
    def client_update_scores(self, payload, Scores):
        """ Create object to store received scores and then copy the data to the standard Scores object """
        NewGameDataScores = pickle.loads(payload)
        Scores.SetNewScores(NewGameDataScores)
        return

    def client_update_hand(self, payload, Handset, GameData):
        Handset.players[GameData.local_player_num] = pickle.loads(payload)
        return
    
    def client_update_won_cards(self, payload, iteration, TeamWonSet):
        """ Receive a set of won cards (payload) and replace local woncards (team 0 or 1 depending on iteration)
        """
        # Undump (result will be a object of identical type than the one sent)
        TeamWonSet.players[iteration] = pickle.loads(payload)
        return
        
    def client_update_played_cards(self, payload, PlayedDeckHand):
        """ Receive the played hand from server (payload) and replace local played hand
        """
        # Undump (result will be a object of identical type than the one sent)
        TmpPlayedHand = Hand.Hand()
        TmpPlayedHand = pickle.loads(payload)
        # Transfer content of hand from temporary object to the one of the game
        PlayedDeckHand.label = TmpPlayedHand.label
        PlayedDeckHand.KeyCode = TmpPlayedHand.KeyCode
        PlayedDeckHand.cards = TmpPlayedHand.cards
        return
        
    def cli_check_master_and_interpret_command(self, command, iteration, payload, PlayedDeckHand, TeamWonSet, Handset, GameData, Scores):
        """ Call the right function according to command
            For command send several time, an "iteration" parameters allow to know in which stage we are
            
            command: a 2-char string with the command
            iteration: 0 for the first time, or more if several time the same command
            payload: The payload received
            
            Return value: True if the result of the command is that the client becomes the master. False otherwise
            
            Note: Non-recognized commands are ignored
        """
        ForceExitWait = False
        
        command_str = str(command, 'UTF-8') # Convert from bytes received to string for comparison
        
        if command_str == self.SrvMesHead["Welcome"]:
            self.client_welcome_infos(payload, GameData)
        if command_str == self.SrvMesHead["PlayedCards"]:
            self.client_update_played_cards(payload, PlayedDeckHand)
        if command_str == self.SrvMesHead["WonCards"]:
            self.client_update_won_cards(payload, iteration, TeamWonSet)
        if command_str == self.SrvMesHead["Hand"]:
            self.client_update_hand(payload, Handset, GameData)
        if command_str == self.SrvMesHead["GameData"]:
            self.client_update_gamedata(payload, GameData)
        if command_str == self.SrvMesHead["YourTurn"]: # The client is now the master for the action
            self.cli_change_state("Master")
            # Only gives the player YourTurn color if we don't want to show an error
            # if GameData.game_board.BackgroundColor != GameData.game_board.BackgroundColorError:
            #     GameData.game_board.BackgroundColor = GameData.game_board.BackgroundColorYourTurn
            print ("Cli cli_check_master_and_interpret_command YourTurn")
        if command_str == self.SrvMesHead["CardValid"]: # The server validate the action, nothing to do except changing state
            # Nothing to do, excep changing the state to indicate the error
            GameData.ErrorState = GameData.ErrorStates.index("NoError")
            # GameData.game_board.BackgroundColor = GameData.game_board.BackgroundColorOk
            print ("Cli cli_check_master_and_interpret_command CardValid")
            self.cli_change_state("WaitServer")
            ForceExitWait = True
        if command_str == self.SrvMesHead["CardInvalid"]: # The client is now the master for the action
            GameData.ErrorState = GameData.ErrorStates.index("NotAllowed")
            # GameData.game_board.BackgroundColor = GameData.game_board.BackgroundColorError
            print ("Cli cli_check_master_and_interpret_command CardInvalid")
            self.cli_change_state("WaitServer") # Wait server for updates (the server will give back the turn later)
            ForceExitWait = True
        if command_str == self.SrvMesHead["Scores"]: # The client has to update its scores
            # If server asks to refresh, we have to go out of the waiting loop to get the refresh done
            self.client_update_scores(payload, Scores)
        if command_str == self.SrvMesHead["Refresh"]: # The client has to update its screen
            # If server asks to refresh, we have to go out of the waiting loop to get the refresh done
            ForceExitWait = True
        
        return ForceExitWait

    
    def cli_send_header(self, HeaderRef, PayloadSize):
        """ This function will send the header and the payload size to the server
        
        HeaderRef: Reference of the header in the associated dictionary
        PayloadSize: Size of the payload that will follow
        """
        
        # Prepare the command and send it
        Command = self.CliMesHead[HeaderRef] # Get header in 2 letters
        bytes_command = bytes(str(Command), 'utf-8')
        # bytes_command_pickle = pickle.dumps(bytes_command) Line probably to me removed
        self.sock.send(bytes_command)
        
        # Prepare the paylaod size and send it
        PayloadSizeStringBytes = bytes(format(PayloadSize, '05d'), 'utf-8') # Converts Payload Size in string of 5 bytes
        self.sock.send(PayloadSizeStringBytes)
        return    

    
    def cli_send_card_selected(self, pos_card):
        """ Called when the user selected a card on the client and need to send that to the server """
        
        # The payload will simply be an integer giving the position of the card in the player's hand, decimal on 2 bytes
        Payload = bytes(format(pos_card, '02d'), 'utf-8')
        PayloadSize = len(Payload)
        
        self.cli_send_header("CardSelected", PayloadSize) # Send Header and message size
        self.sock.send(Payload) # Send the payload (card position)
        return
        
    def ListenAndInterpretCommands(self, PlayedDeckHand, TeamWonSet, Handset, GameData):
        """ Receives in a loop data with Command/Size/payload information """
        ReceptionStates = ["GetCommand", "GetSize", "GetPayload"]
        # Received = {"GetCommand":0, "GetSize": 0, "GetPayload" :0}
        RecState = ReceptionStates.index("GetCommand") # Initialize the state
        ForceExitLoop = False # When turn true, the loop will exit to allow refresh
        # chunks = []
        PreviousCommand = "" # Will store the previous command
        Iteration = 0 # Iteration will be increased if se receive several time the same command
        SizeToGet = 1024 # Default value in case, never used normally

        # When entering this function, the global client state is a slave, waiting for server inputs
        self.cli_change_state("WaitServer")

        while (not self.state == self.CliStates.index("Master")) and not ForceExitLoop: # loop until we get the Hand back or at the end of the first init
            # Set expected message size based on received command (when not payload)
            if RecState == ReceptionStates.index("GetCommand"):
                SizeToGet = 2
            if RecState == ReceptionStates.index("GetSize"):
                SizeToGet = 5
            
            data = self.sock.recv(SizeToGet)
            if not data:
                break
            
            # Check if we are waiting the command
            if (RecState == ReceptionStates.index("GetCommand")):
                print('GetCommand Received', data)
                mysize = len(data)
                if mysize == 2: # We received the two letters
                    command = data
                    # Increase iteration if same command, and store latest command
                    if PreviousCommand == command:
                        Iteration = Iteration + 1
                    else:
                        Iteration = 0
                    PreviousCommand = command
                    data = "" # Empty data by principle (Not sure it is needed)
                    RecState = ReceptionStates.index("GetSize")
                    continue
                else:
                    continue
                    
            # Check if we are waiting the payload size
            if RecState == ReceptionStates.index("GetSize"):
                print('GetSize Received', data)
                mysize = len(data)
                if mysize == 5: # We received the payload size on 5 bytes, string
                    SizeToGet = int(data)
                    # print('The payload will be of ', str(SizeToGet) , ' bytes')
                    data = ""
                    if (SizeToGet == 0): # No payload: Call now the function to interpret the command
                        if self.cli_check_master_and_interpret_command(command, Iteration, data, PlayedDeckHand, TeamWonSet, Handset, GameData, GameData.Scores):
                            # If returned true, this means it is OK, but we need to leave the wait loop
                            ForceExitLoop = True
                        RecState = ReceptionStates.index("GetCommand")
                    else:
                        RecState = ReceptionStates.index("GetPayload")
                        continue
                else:
                    continue
            
            # Check if we are waiting the payload
            if (RecState == ReceptionStates.index("GetPayload")):
                # print('GetPayload Received', data)
                mysize = len(data)
                # print('Payload size: ', mysize, ' Payload expected:', SizeToGet)
                if mysize == SizeToGet: # We received the full payload, let's work with it
                    # print('Full payload received')
                    if self.cli_check_master_and_interpret_command(command, Iteration, data, PlayedDeckHand, TeamWonSet, Handset, GameData, GameData.Scores):
                        # If returned true, this means it is OK, but we need to leave the wait loop
                        ForceExitLoop = True
                    command = data
                    data = ""
                    RecState = ReceptionStates.index("GetCommand")
                else:
                    continue
        
        return