""" This file is part of a sample of the swiss Jass game implementation

    Classes in that file manage objects and methods related Preferences/Settings of the game
"""

from tkinter import *

class Preferences:
    NetworkModesList = ["Standalone", "Server", "Client"]

    def __init__(self):
        """ Default Preferences """
        self.LockDisplay = False # If LockDisplay, request key before displaying player cards
        self.ShowAllCards = False # For debug purpose: if True, show all players cards
        self.ShowCardsFan = False # Show cards as Fan (éventail)
        self.NetworkMode = self.NetworkModesList.index("Standalone")
        self.ServerIP = "127.0.0.1" # Server to connect to when in client mode
        self.ServerPort = 65432 # Server port when in client mode
        self.ShowPrefWindowAtStart = True # Can be set to true manually for generating binary version

    
    def PrepareWindowVariables(self):
        self.PrefWin = Tk() # Create The TK Window
        # List of variables which will be used as variable for each Window elements
        self.TkVarShowAllCards = IntVar(self.PrefWin) # A TK integer
        self.TkVarServerIP = StringVar(self.PrefWin) # A TK string
        self.TkVarServerPort = StringVar(self.PrefWin) # A TK string
        self.TkVarNetworkMode = StringVar(self.PrefWin) # A TK string
        self.TkVarLockDisplay = BooleanVar(self.PrefWin) # A TK boolean
        self.TkVarShowAllCards = BooleanVar(self.PrefWin) # A TK boolean ShowAllCardsCheckbox
    
    def Cancelled(self):
        print ("Cancellation selected")
        self.PrefWin.destroy() # Destroy the window
    
    def Validated(self):
        print ("Validation selected")
        # Get all check boxes
        self.ShowAllCards = self.TkVarShowAllCards.get()
        self.LockDisplay = self.TkVarLockDisplay.get()
        
        # Get all text boxes
        self.ServerIP = self.TkServerIP.get()
        self.ServerPort = self.TkServerPort.get()
        
        # Get Drop list value
        self.NetworkMode = self.NetworkModesList.index(self.TkVarNetworkMode.get())
        
        self.PrefWin.destroy() # We stored all prefs, destroy the window
    
    def DisplayPrefWindow(self):
        """ Open a window to allow preference edition"""
        
        self.PrepareWindowVariables() # Prepare all TK variables
        
        self.PrefWin.title("Préférences jeu de Jass")
        
        Currow = 0 # Current row       
        
        # LockDisplay checkbox
        self.TkVarLockDisplay.set(self.LockDisplay) #set check state
        self.TkLockDisplay = Checkbutton(self.PrefWin, text='Vérouiller affichage cartes', var=self.TkVarLockDisplay)
        self.TkLockDisplay.grid(column=0, row=Currow, sticky=W)
        Currow += 1
        
        # All cards checkbox
        self.TkVarShowAllCards.set(self.ShowAllCards) #set check state
        self.TkShowAllCards = Checkbutton(self.PrefWin, text='Montrer toutes les cartes', var=self.TkVarShowAllCards)
        self.TkShowAllCards.grid(column=0, row=Currow, sticky=W)
        Currow += 1
        
        # IP server
        self.TkServerIPLabel = Label(self.PrefWin, text="IP du serveur:")
        self.TkServerIPLabel.grid(column=0, row=Currow, sticky=E)
        self.TkServerIP = Entry(self.PrefWin, width=15)
        self.TkServerIP.insert(END, self.ServerIP) # Initialize with current pref
        self.TkServerIP.grid(column=1, row=Currow, sticky=W)
        Currow += 1
        
        # Port server
        self.TkServerPortLabel = Label(self.PrefWin, text="Port du serveur:")
        self.TkServerPortLabel.grid(column=0, row=Currow, sticky=E)
        self.TkServerPort = Entry(self.PrefWin, width=6)
        self.TkServerPort.insert(END, self.ServerPort) # Initialize with current pref
        self.TkServerPort.grid(column=1, row=Currow, sticky=W)
        Currow += 1
        
        # Set application mode
        self.TkNetworkModeLabel = Label(self.PrefWin, text="Mode:")
        self.TkNetworkModeLabel.grid(column=0, row=Currow, sticky=W)
        self.TkVarNetworkMode.set(self.NetworkModesList[self.NetworkMode]) # default value
        self.TkNetworkMode = OptionMenu(self.PrefWin, self.TkVarNetworkMode, self.NetworkModesList[0], self.NetworkModesList[1], self.NetworkModesList[2])
        self.TkNetworkMode.grid(column=1, row=Currow, sticky=W)
        Currow += 2
        
        # Create Cancel button
        self.btn_cancel = Button(self.PrefWin, text="Annuler", command=self.Cancelled)
        self.btn_cancel.grid(column=0, row=Currow)
        
        # Create Validation button
        self.btn_validate = Button(self.PrefWin, text="Valider", command=self.Validated)
        self.btn_validate.grid(column=2, row=Currow)
        
        self.PrefWin.mainloop() # Wait that the window is destroyed (after validatino or cancellation)