""" This file is part of a sample of the swiss Jass game implementation

    Classes in that file manage all socket and connection related tasks for a server
"""

# from asyncio.windows_events import NULL
import socket, selectors, types, sys, pickle
import time
import GameData

class WelcomeInfosToSend:
    """ Class containing only data to be sent to clients at the game start (sent only once)"""
    def __init__(self, PlayerNumber=0):
        self.PlayerNumber = PlayerNumber # Current player

class DataGameToSend:
    """ Class containing only data to be sent to clients about the game """
    def __init__(self, current_player, atout, nb_players, latest_winner):
        self.current_player = current_player # Current player
        self.atout = atout # Atout of the game
        self.nbplayers = nb_players # Number of players in the game
        self.latest_winner = latest_winner # Will contain the latest Winner in order to know which 4-cards to show

class GameStateToSend:
    """ Class containing only object with game state change """
    def __init__(self, current_state):
        self.state = GameData.GameData.GameStates.index(current_state)

class AnnoncesToSend:
    """ Class containing only the annonces of the 4 players """
    def __init__(self, handset):
        self.annonces_to_send = [] # Create empty list. This will be a list of list. First level: player. Second level: list of cards
        self.team_annonce = handset.TeamAnnonce # contain the team number for which we should display the annonces
        for player in range(0,4):
            self.annonces_to_send.append([]) # Create the list before using append
            for cardID in range(0, len(handset.players[player].annonces_cards)):
                self.annonces_to_send[player].append(handset.players[player].annonces_cards[cardID])
        return

class SrvCom:
    """ Class for the server mode, containing all information about clients connected in case of run in server mode"""
    
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server 

    SrvMesHead = {"Welcome" : "WE", \
                    "PlayedCards": "PC", \
                        "WonCards" : "WC", \
                            "Hand": "HA", \
                                "GameData" : "GD", \
                                    "YourTurn" : "YT", \
                                        "CardValid" : "CV", \
                                            "CardInvalid" : "CI", 
                                                "Refresh" : "RE", \
                                                    "Scores" : "SC", \
                                                        "ForceState" : "FS", \
                                                            "CardsAnnonces" : "CA"} # From Server Messages types (Str) and headers (2 chars)


    SrvStates = ["Init", "Master", "WaitClient"] # Possible states of the server mode
    CliMesHead = {"CardSelected" : "CS", "AnnoncesValidated" : "AV"} # Messages that a client can send to the server. Scores is used only if local even changes the player's score
    
    def __init__(self):
        self.conn = [] # Create an empty list to store future connection references. ID will be shifted: 1st connected will have index 0
        self.SrvState = 0 # Default start state
    
    def srv_change_state(self, NewState):
        if self.SrvState != self.SrvStates.index(NewState):
            print("Server becomes", NewState)
        self.SrvState = self.SrvStates.index(NewState)
        

    def srv_send_header(self, ConID, HeaderRef, PayloadSize):
        """ This function will send the header
        
        HeaderRef: Reference of the header in the associated dictionary
        ConID: ID of the connection in the list
        PayloadSize: Size of the payload that will follow
        """
        
        # Prepare the command
        Command = self.SrvMesHead[HeaderRef] # Get header in 2 letters
        print ('Send Command: ', Command, ' to client: ', ConID)
        if (ConID < 0):
            print ('ERROR')
        bytes_command = bytes(str(Command), 'utf-8')
        bytes_command_pickle = pickle.dumps(bytes_command)
        self.conn[ConID].send(bytes_command)
        
        # Prepare the paylaod size
        PayloadSizeStringBytes = bytes(format(PayloadSize, '05d'), 'utf-8') # Converts Payload Size in string of 5 bytes
        # Send the 5 bytes of "PayloadSizeString", which is a string of 5 characters
        self.conn[ConID].send(PayloadSizeStringBytes)
        return    

    
    def srv_send_game_data(self, DataGame):
        """ This function will send all game data necessary to each client, data which are defined in the class DataGameToSend

        """
        DataToSend = pickle.dumps(DataGameToSend(DataGame.current_player, DataGame.atout, DataGame.nbplayers, DataGame.latest_winner))
        for ConID in range(0,len(self.conn)):
            PayloadSize = len(DataToSend)
            self.srv_send_header(ConID, "GameData", PayloadSize)         
            self.conn[ConID].send(DataToSend) # Send the payload
    
    def srv_send_force_state(self, NewState, AvoidClient):
        """ This function will send all game data necessary to each client, data which are defined in the class DataGameToSend

            Inputs:
                NewState: New state to be sent to client
                AvoidClient: avoid update to the mentionne client ID (nothing to avoid if value is -1)
        """
        # Create object to send
        ObjectToSend = GameStateToSend(NewState)
        DataToSend = pickle.dumps(ObjectToSend)
        for ConID in range(0,len(self.conn)):
            if ConID != AvoidClient: # Check in case we need to avoid client
                PayloadSize = len(DataToSend)
                self.srv_send_header(ConID, "ForceState", PayloadSize)         
                self.conn[ConID].send(DataToSend) # Send the payload

    def srv_send_annonces(self, handset):
        """ This function will send all annonces to the clients for displaying them """
        # Create object to send
        ObjectToSend = AnnoncesToSend(handset)
        DataToSend = pickle.dumps(ObjectToSend)
        for ConID in range(0,len(self.conn)):
            PayloadSize = len(DataToSend)
            self.srv_send_header(ConID, "CardsAnnonces", PayloadSize)         
            self.conn[ConID].send(DataToSend) # Send the payload

    def srv_send_scores(self, Scores):
        """ This function will send all game data necessary to each client, data which are defined in the class DataGameToSend

        """
        DataToSend = pickle.dumps(Scores)
        for ConID in range(0,len(self.conn)):
            PayloadSize = len(DataToSend)
            self.srv_send_header(ConID, "Scores", PayloadSize)         
            self.conn[ConID].send(DataToSend) # Send the payload

    def srv_send_refresh(self):
        """ This function will send a refresh command to all clients
        """
        for ConID in range(0,len(self.conn)):
            PayloadSize = 0
            self.srv_send_header(ConID, "Refresh", PayloadSize) 
    
    def srv_send_card_valid(self, CurrentPlayer):
        """ This function will send the command to confirm the selected card was valid
        
        CurrentPlayer: The current player (so the connection ID is CurrentPlayer - 1)
        """
        self.srv_send_header(CurrentPlayer-1, "CardValid", 0)         
            
    def srv_send_card_invalid(self, CurrentPlayer):
        """ This function will send the command to confirm the selected card was valid
        
        CurrentPlayer: The current player (so the connection ID is CurrentPlayer - 1)
        """
        self.srv_send_header(CurrentPlayer-1, "CardInvalid", 0)    
    
    def srv_send_other_cards(self, PlayedDeckHand, TeamWonSet):
        """ This function will send to each connected client:
        * The list of played cards
        * The list of won cards per team
        """
        for ConID in range(0,len(self.conn)):
            # First send the list of currently played cards
            Data = pickle.dumps(PlayedDeckHand)
            PayloadSize = len(Data)
            self.srv_send_header(ConID, "PlayedCards", PayloadSize)
            self.conn[ConID].send(Data) # Send the payload of played cards
            
            Data = pickle.dumps(TeamWonSet.players[0])
            PayloadSize = len(Data)
            self.srv_send_header(ConID, "WonCards", PayloadSize)
            self.conn[ConID].send(Data) # Send the payload of played cards
            
            # Finally, send the list of Won cards for team 1
            Data = pickle.dumps(TeamWonSet.players[1])
            PayloadSize = len(Data)
            self.srv_send_header(ConID, "WonCards", PayloadSize)
            self.conn[ConID].send(Data) # Send the payload of played cards
            
    
    def srv_send_hands(self, handset, PlayedDeckHand, TeamWonSet, DataGame):
        """ This function will send the hand of each player connected remotely """
        
        for idx in range(len(self.conn)):
            # Assumption 1: Server is player 0, and connected players are from 1 to max players
            # Assumption 2: The list of connections are in the same order ==> Position + 1 = Player Number
            
            data_string = pickle.dumps(handset.players[idx+1])
            PayloadSize = len(data_string)
            self.srv_send_header(idx, "Hand", PayloadSize)
            # Send players hand corresponding to idx player
            if len(self.conn) > idx: # Check that connection exists in the table
                self.conn[idx].send(data_string)
    
    def srv_send_welcome_infos(self, DataGame):
        """ This function will send Welcome info, espcially the player number attributed to each connection

        """
        WelcomInfos = WelcomeInfosToSend() # Create one object with fake parameters that we will reuse for all connected clients
        
        for ConID in range(0,len(self.conn)):
            WelcomInfos.PlayerNumber = ConID + 1
            DataToSend = pickle.dumps(WelcomInfos)
            PayloadSize = len(DataToSend)
            self.srv_send_header(ConID, "Welcome", PayloadSize)         
            # time.sleep(1)
            self.conn[ConID].send(DataToSend) # Send the payload
    
    def srv_send_all_data(self, handset, DataGame, TeamWonSet, PlayedDeckHand):
        """ This function will call all subfunction to send all necessary data to all connected clients """
        self.srv_send_game_data(DataGame)
        self.srv_send_other_cards(PlayedDeckHand, TeamWonSet)
        self.srv_send_hands(handset, PlayedDeckHand, TeamWonSet, DataGame) # Note: This can only be called after welcome infos have been sent
        self.srv_send_scores(DataGame.Scores)
        self.srv_send_refresh() # To force clients refresh
        
    def srv_execute_card_selected_command(self, TeamWonSet, CardPos, Handset, PlayedDeck, DataGame, Scores):
        """ This function will execute the necessary actions based on card clicked. It aslo send back a feed-back to the client and request the refresh """
        # Store Current Player value for the execution (in case it changes during the operations)
        FctCurPlayer = DataGame.current_player
        # Execute the operations as if we were in standalone mode
        if DataGame.is_this_game_state("SelAtout") or DataGame.is_this_game_state("SelAtoutChibre"):
            DataGame.atout = Handset.players[FctCurPlayer].cards[CardPos].suit # Store the chosen atout
            if Handset.AnnoncesFullCheck(DataGame, Scores): # Check if all users annonces, compare value and add points to the team if needed
                DataGame.set_game_state("ShowAnnonces") # Change State to ShowAnnonces
                DataGame.SrvComObject.srv_send_all_data(Handset, DataGame, TeamWonSet, PlayedDeck) # Send all data include new state and cards of annonce
                DataGame.SrvComObject.srv_send_annonces(Handset)
                DataGame.SrvComObject.srv_send_force_state("ShowAnnonces", -1) # Send all data include new state and cards of annonce
            else:
                DataGame.set_game_state("Play") # Change State to Play
            self.srv_send_game_data(DataGame) # Send update of the data game (including atout) to everybody
            self.srv_send_scores(Scores) # Send updated score in case of annonces
            self.srv_send_refresh() # To force clients refresh
        elif DataGame.is_this_game_state("Play"):
            if Handset.action_card_selected(FctCurPlayer, CardPos, DataGame, PlayedDeck, TeamWonSet, Scores): # Note: action_card_selected function will update player number
                # The action was done successfully
                self.srv_send_card_valid(FctCurPlayer)
            else:
                # The action was refused
                self.srv_send_card_invalid(FctCurPlayer)
            self.srv_send_all_data(Handset, DataGame, TeamWonSet, PlayedDeck) # Send update of all data after player played
        return
    
    def srv_listen_commands_and_execute(self, CurrentPlayer, Handset, PlayedDeck, TeamWonSet, DataGame, Scores):
        """ This function will listen on the command returned by the client and act upon
        Assumption: The client will only return ONE command
        """
        data = self.conn[CurrentPlayer - 1].recv(2) # Use CurrentPlayer -1, because player 1 has connection ID 0
        if not data:
            return
        command_str = str(data, 'UTF-8') # Convert from bytes received to string for comparison
        
        print ('Received Command: ', command_str, ' from client: ', CurrentPlayer - 1)
        if command_str == "00":
            print ("Error message")
        # Read the size of the message
        Size = self.conn[CurrentPlayer - 1].recv(5) # Size is coded in string on 5 characters
        SizeToGet = int(Size)
        if (SizeToGet > 0): # Only get payload if size > 0
            Payload = self.conn[CurrentPlayer - 1].recv(SizeToGet) # Size is coded in string on 5 characters
        if command_str == self.CliMesHead["CardSelected"]:
            # Card position is normally coded on a 2-chars string
            CardPos = int(str(Payload, 'UTF-8')) # Convert from bytes received to integer
            # print ("server: card select is position", str(CardPos))
            self.srv_execute_card_selected_command(TeamWonSet, CardPos, Handset, PlayedDeck, DataGame, Scores) # Execute action (including feed-back to the client)
        if command_str == self.CliMesHead["AnnoncesValidated"]: # Client clicked to remove annonces
            # No payload expected for this commmand
            DataGame.set_game_state("Play") # Change State to Play
            # Force refresh and telling the client is done automatically later, except the change of state.
            self.srv_send_force_state("Play", CurrentPlayer - 1)


    def srv_give_master_and_listen_commands(self, Handset, PlayedDeck, TeamWonSet, DataGame, Scores):
        """ This function will give the master to the player in turn (via its connection) and wait for client message to continue
        
        DataGame: Information about the game (needed: current player)
        """
        # Temporarily (not optimal), send all data before giving turn. This ensures that data like current player is updated for the client
        self.srv_send_all_data(Handset, DataGame, TeamWonSet, PlayedDeck)
        # First Send the message to the client in turn that he becomes temporarilly the master
        self.srv_send_header(DataGame.current_player - 1, "YourTurn", 0) # -1 because the first connection (index 0) corresponds to player 1
        # Then wait for message from the client, and execute necessary actions
        self.srv_listen_commands_and_execute(DataGame.current_player, Handset, PlayedDeck, TeamWonSet, DataGame, Scores)
        # We don't know what happened, but let's resend all data to clients
        self.srv_send_all_data(Handset, DataGame, TeamWonSet, PlayedDeck)
         

    def server_wait_all_players(self, NbPlayers):
        """ This function will wait that all players (3 expected) are connected to it before exiting
        
        self: An empty list which will contain connection data when connections will happen
        NbPlayer: Nb connection to wait on (usually: 3)
        
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.bind((self.HOST, self.PORT))

            clients = list()
            for idx in range(NbPlayers): # times the loop to wait for all clients
                s.listen()
                conn, addr = s.accept()
                self.conn.append(conn)
                print('client_{} connected: {}'.format(idx, addr))
