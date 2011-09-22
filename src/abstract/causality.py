#!/usr/bin/python

from engine.ormapping import Persistent, Reference, BackRef

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


class Signal (object):

    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Base class for Signals. Doesn't implement anything at the
    moment. Made for future development and downward compatibility
    """
    
    pass

class M2M_EnviromentEmitter (Persistent):

    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    [internal] Many-to-Many mapping of CausalEnviroments and SignalEmitters.
    """
    
    __class_table__ = "M2M_EnviromentEmitter"

    enviroment = Reference()    
    emitter    = Reference()


    def __init__ (self, enviroment, emitter):
        Persistent.__init__ (self)
        self.enviroment = enviroment
        self.emitter = emitter

class M2M_EnviromentListener (Persistent):
 
    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    [internal] Many-to-Many mapping of CausalEnviroments and SignalListeners.
    """
    
    __class_table__ = "M2M_EnviromentListener"

    enviroment = Reference()    
    listener   = Reference()

    def __init__ (self, enviroment, listener):
        Persistent.__init__ (self)
        self.enviroment = enviroment
        self.listener = listener


class CausalEnviroment (Persistent):
    
    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    A Collection to connect SignalEmitters and SignalListeners.
    Should only be needed by the Room class
    """
    
    emitterlinks  = BackRef (M2M_EnviromentEmitter,"enviroment")
    listenerlinks = BackRef (M2M_EnviromentListener,"enviroment")
    
    def __init__ (self):
        Persistent.__init__(self)
        
    def addEmitter (self, e):
        
        """ Adds SignalEmitter e to enviroment """

        link = M2M_EnviromentEmitter(self,e)
    
    def removeEmitter (self, e):
        
        """ Removes SignalEmitter e from enviroment """
        
        links = self.emitterlinks
        for l in links:
            if l.emitter == e:
                l.__delete__()
    
    def getEmitters (self):
        return map(lambda x : x.emitter, self.emitterlinks)

    emitters = property(fget=getEmitters,\
                        doc="SignalEmitters placed in this enviroment")

    def addListener (self, l):

        """ Adds SignalListener l to enviroment """
        
        link = M2M_EnviromentListener(self,l)
    
    def removeListener (self, l):
        
        """ Removes SignalListener l from enviroment """
        
        links = self.listenerlinks
        for l in links:
            if l.emitter == l:
                l.__delete__()
    
    def getListeners (self):
        return map(lambda x : x.listener, self.listenerlinks)

    listeners = property(fget=getListeners,\
                         doc="SignalListeners placed in this enviroment")


    
 
 
class SignalEmitter (Persistent):

    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Emits Signals
    """

    enviromentlinks = BackRef(M2M_EnviromentEmitter,"emitter")
     
    def __init__ (self):
        Persistent.__init__(self)

    def emitExitSignal (self):
        """ [event method] Gets invoked, before player leaves
        room, if he/she has the emitter with him/her """
        pass
    
    def emitEntrySignal (self):
        """ [event method] Gets invoked, after player left
        room, if he/she has this emitter with him/her """
        pass

    def getEnviroments (self):
        return map(lambda x : x.enviroment, self.enviromentlinks)

    enviroments = property(fget = getEnviroments,
                           doc  = "Enviroments to which this emitter is linked")

    def emit (self,signal):
        """ 
        Emits signal to all listeners in all linked enviroments
        """
        for e in self.enviroments :
            for l in e.listeners:
                l.signalReceived(signal)
        
        
class SignalListener (Persistent):
     
    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Listens to Signals. Interface specification.
    """
 
     
    def __init__ (self): 
        Persistent.__init__(self)

    def signalReceived (self,signal):
        
        """ 
        Will be called, when a emitter in a linked enviroment
        shares a signal.
        
        @Warning: You have to do a type/attribute check of the
        signal in this class to check, if it is suitable for
        this listener
        
        @raise NotImplementedError: always
        """ 
        
        raise NotImplementedError("Lack of signalReceived method")


        
        