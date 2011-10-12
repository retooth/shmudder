#!/usr/bin/python

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

from engine.ormapping import Persistent, Reference, BackRef


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


class M2M_RoomEmitter (Persistent):

    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    [internal] Many-to-Many mapping of Rooms and SignalEmitters.
    """
    
    room    = Reference()    
    emitter = Reference()

    def __init__ (self, room, emitter):
        Persistent.__init__ (self)
        self.room = room
        self.emitter = emitter


class M2M_RoomListener (Persistent):
 
    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    [internal] Many-to-Many mapping of Rooms and SignalListeners.
    """
    
    room = Reference()    
    listener = Reference()

    def __init__ (self, room, listener):
        Persistent.__init__ (self)
        self.room = room
        self.listener = listener


class SignalEmitter (Persistent):

    """
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Emits Signals
    """

    roomlinks = BackRef(M2M_RoomEmitter, "emitter")
     
    def __init__ (self):
        Persistent.__init__(self)


    def getTransmissionArea (self):
        area = []
        for link in self.roomlinks:
            area.append(link.room)
        if 'location' in dir(self):
            area.append(self.location)
        return area

    transmissionarea = property(fget = getTransmissionArea,
                                doc  = "Rooms to which this emitter is linked")


    def emit (self, signal):
        """ Emits signal to all listeners in all linked rooms"""
        for room in self.transmissionarea :
            for listener in room.listeners:
                listener.signalReceived(signal)
        
    
    def emitInRoom (self, signal, room):
        """ Emits signal to all listeners in room"""
        for listener in room.listeners:
            listener.signalReceived(signal)
        
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


    def signalReceived (self, signal): 
        """ 
        Will be called, when a emitter in a linked room
        shares a signal.
        
        @Warning: You have to do a type/attribute check of the
        signal in this class to check, if it is suitable for
        this listener
        
        @raise NotImplementedError: always
        """ 
        raise NotImplementedError("Lack of signalReceived method")


        
        