#!/usr/bin/python

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory

from abstract.exceptions import ContextError

#    This file is part of Shmudder.
#
#    Shmudder is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Shmudder is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Shmudder.  If not, see <http://www.gnu.org/licenses/>.


class ShmudderProtocol(LineReceiver,object):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Protocol for the MudbathFactory. Every protocol
    has a corresponding GameHandler (on init: LoginHandler)
    
    Game designer must set class vars loginhandler and registerhandler 
    to suitable types
    """
    
    loginhandler    = None
    registerhandler = None
    
    def __init__(self):
        self._handler = None

    def setHandler(self, h):
        h.client = self
        self._handler = h
        h.__contextinit__()
        
    def getHandler(self):
        return self._handler 

    handler = property(fget = getHandler,\
                       fset = setHandler,\
                       doc  = "Protocols current handler")
    
    def send (self,data):
        
        """ 
        Sends data back to the client
        """
        
        self.transport.write(data+"\r\n")
    
    def connectionMade(self):
        
        """ 
        will be called, when a connection is made. it acquaints the
        protocol with the factory and initializes the login handler
        """

        # shake hands
        self.factory.clients.append(self)
        
        # initialize login handler
        lh = self.__class__.loginhandler()
        self.handler = lh

    def lineReceived (self,data):
        
        """ 
        will be called, when data arrives.
        """

        # strip newlines and stuff
        data = data.rstrip()
        
        # let the handler handle it
        handler = self.handler
        handler.handle(data)
        
    def connectionLost(self, reason):
 
        """ Will be called, when client disconnects """
 
        self.factory.clients.remove(self)
        
        # save last location
        if "location" in dir(self.handler):
            self.handler.lastlocation = self.handler.location
            self.handler.location     = None


class ShmudderFactory(ServerFactory):

    protocol = ShmudderProtocol

    def __init__(self):
        self.clients = []


class GameHandler (object):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    GameHandler saves relevant states of the Player
    and parses commands by context 
    """
    
    
    def __init__ (self):
        self._context  = None
        self.client = None
        
    def setContext(self,c):
        
        """ 
        Sets new context and invokes goodbye/welcome methods
        """
    
        # if old context exists, show goodbye messages
        if self._context != None :
            self._context.showGoodBye(self)
        
        # set new context and show welcome message
        self._context = c
    
        # if new context exists, show welcome message
        if self._context != None :
            self._context.showWelcome(self)
                
    def getContext (self):
   
        """ 
        Gets the current context
        @rtype: context
        """
   
        return self._context        

    context = property(getContext,setContext)

    def handle (self, command):
        
        """ 
        Handles a command by the currently active context. 
        In particular, parses the raw string into an action 
        object and handles game exceptions (e.g. if an item 
        was not found)
        """
        
        # try to do the action
        try:
            # get the current context and parse command
            actionf, regex, arguments  = self.context.parse(command)
            actionf(self,regex,arguments)
        except ContextError as ce :
            # action is not possible for some reason:
            # handle the exception
            self.context.handle(self,ce)
            

    def receiveMessage (self, message):
        
        """ entry point for messages, that returned from the game """
        
        client = self.client
        
        if not client:
            return
        
        client.send(message)



class LoginHandler (GameHandler):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Special GameHandler for Login. Game Developer must
    set logincontext and passwordcontext class vars
    to suitable types
    """

    logincontext    = None
    passwordcontext = None

    def __init__ (self):
        GameHandler.__init__(self)
        self.wannabe = None
    
    def __contextinit__ (self):
        cls = type(self)
        self.context = cls.logincontext()
    
    def switchToRegisterHandler (self):
        client = self.client
        client.handler = client.__class__.registerhandler()
        


class RegisterHandler (GameHandler):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Special GameHandler for Register. Game Developer must
    set playerchoice, passwordchoice and namechoice to
    suitable (context) types    
    """

    
    playertypes     = []
    characterchoice = None
    passwordchoice  = None
    namechoice      = None
    
    def __init__ (self):
        GameHandler.__init__(self)
        
        self.wannabe = None 
        """ Player object after type is chosen """
        
        cls = type(self)
        pwc = cls.passwordchoice()
        nmc = cls.namechoice()
        self._contextq = [nmc,pwc]

    def __contextinit__ (self):
        cls = type(self)
        plc = cls.characterchoice()
        self.context = plc

    def addChoice (self, context):
        """ Adds an additional choice""" 
        
        self._contextq.insert(-2, context)

    def nextContext (self):
        self.context = self._contextq.pop(0)
        
    def emergeWannabe (self,t):
        self.wannabe = t()
    
    @classmethod
    def callPlayerType (cls,key):
    
        types = cls.playertypes
        
        for t in types :
            if key in t.typekeywords :
                return t
                break
            
        return None
