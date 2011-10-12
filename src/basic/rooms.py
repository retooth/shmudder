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


from engine.ormapping import Boolean, Reference, BackRef
from abstract.perception import Addressable, Perceivable, callAdressables
from abstract.causality import SignalEmitter, SignalListener
from abstract.causality import M2M_RoomEmitter, M2M_RoomListener
from basic.characters import CharacterCollection
from basic.items import ItemCollection
from random import choice
from basic.exceptions import NoSuchDirection, AmbigousDirection

class Exit (Addressable):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Room Exit
    """
    
    anchor    = Reference()
    direction = Reference()
    
    def __init__ (self, anchor, direction):
        Addressable.__init__(self)
        self.anchor    = anchor
        self.direction = direction
        
        
    def __str__ (self):
        return self.skeywords[0]



class Room (Perceivable,
            CharacterCollection,
            ItemCollection):
    
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Basic class for dungeon rooms.
    """

    exits = BackRef(Exit,"anchor")
    dungeon = Reference()
    
    emitterlinks  = BackRef (M2M_RoomEmitter, "room")
    listenerlinks = BackRef (M2M_RoomListener, "room")
    

    def __init__(self):
        Perceivable.__init__(self)
        CharacterCollection.__init__(self)
        ItemCollection.__init__(self)
    
    
    def getAll (self):
        all = self.allitems
        all += self.details
        all += self.characters
        for c in self.characters:
            all += c.inventory.allitems
        return all
    
    all = property(fget = getAll,
                   doc  = "Everything in this room")
    
    def getLocation (self):
        return self
    
    location = property(getLocation)


    def addEmitter (self, e):
        """ Adds a static (!) SignalEmitter e to this room """
        link = M2M_RoomEmitter(self, e)
    
    
    def removeEmitter (self, e):
        """ Removes static (!) SignalEmitter e from this room """
        links = self.emitterlinks
        for link in links:
            if link.emitter == e:
                del link
    
    
    def getEmitters (self):
        emitters = []
        for link in self.emitterlinks:
            emitters.append(link.emitter)
        for thing in self.all:
            if isinstance(thing, SignalEmitter):
                emitters.append(thing)
        return emitters

    emitters = property(fget = getEmitters, \
                        doc  = "SignalEmitters linked to this room")


    def addListener (self, l):
        """ Adds static(!) SignalListener l to this room """
        link = M2M_RoomListener(self, l)
  
    
    def removeListener (self, l):      
        """ Removes (static) SignalListener l from this room """
        links = self.listenerlinks
        for link in links:
            if link.emitter == l:
                del link
    
    
    def getListeners (self):
        listeners = []
        for link in self.listenerlinks:
            listeners.append(link.listener)
        for thing in self.all:
            if isinstance(thing, SignalListener):
                listeners.append(thing)
        return listeners

    listeners = property(fget = getListeners, \
                         doc  = "SignalListeners linked to this room")


        
    def addCharacter(self, c):
        
        """ 
        Adds character c to the room
        """
        
        CharacterCollection.addCharacter(self, c)
        c.location = self


    def removeCharacter(self, c):        
        """ Removes character c from the room """
        CharacterCollection.removeCharacter(self, c)
    
####################       
      
    def __contains__ (self, i):
        items = self.items
        chars = self.characters
        details = self.details
        return i in (items+chars+details)
    
    
    def receiveMessage (self, message, exceptc=[]):
        """ 
        shares message with players in the room.
        @param exceptc: a list of players, that will be omitted
        """
        for character in self.characters:
            if character not in exceptc:
                character.receiveMessage(message)
    
    
    def hasExit (self, exitname):
        """ For convenience """
        if exitname in self.exits:
            return True
        return False
    
    
    def connect(self, neighbor, *dirkeys):
        """
        Connects another room to this one.
        @param *dirkeys: keywords for direction
        """
        rexit = Exit(self, neighbor)
        for keyword in dirkeys :
            rexit.addSingularKeyword(keyword)
        

    def showLong (self, actor):
        """ This method is triggered by the 'look around'
        command. It implements the standard MUD view of
        a room (Description of the Room, List of Items,
        List of Characters). """ 
        self.showShort(actor)
        self.showItems(actor)
        self.showDetails(actor)
        self.showOtherCharacters(actor)


    def leave(self, actor, keyword):        
        """ This method is called, when a player decides
        to exit the room by direction keyword. """
        
        # TODO: party autofollow
        
        exits = callAdressables(keyword, self.exits)
        
        if not exits:
            raise NoSuchDirection("")
        
        if len(exits) > 1:
            raise AmbigousDirection("")
    
        newplace = exits[0].direction
        
        # quest dungeons
        if newplace.dungeon and self.dungeon != newplace.dungeon:
                
            partyident = actor.party.identifier
            clone = newplace.dungeon.getClone(partyident)
                
            # reattach room
            # TODO: sure backRefs are index safe ?
            if clone != newplace.dungeon :
                rindex = newplace.dungeon.rooms.index(newplace)
                newplace = clone.rooms[rindex]
            
        self.removeCharacter(actor)
        newplace.addCharacter(actor)
        
        actor.locationChanged(self, newplace, keyword)
        
        for item in actor.inventory.items:
            item.locationChanged(self, newplace, keyword)
        

    
    def leavePanically (self, actor):
        """ convenience method to leave the
        room in a random direction """
        if self.exits :
            direction = choice(self.exits)
            self.leave(actor, direction)
        
    
    def leaveVeryPanically (self, actor, panic):
        """ recursive version of leavePanically.
        recursion depth is described as int in panic
        """
        # do as many room changes
        # as said in panic
        if panic > 0 :
            
            # leave panically
            self.leavePanically(actor)
            
            # recursion
            newroom = actor.location
            newroom.leaveVeryPanically(actor, (panic-1))

        
    def teleport (self, actor, hop):
        """ convenience method to jump to another room """
        self.removeCharacter(actor)
        hop.addCharacter(actor)
        
    
class UniqueRoom (Room):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Singleton version of Room. Use a subclass of this for
    Player's defaultlocation or dungeon transition rooms
    
    @warning: Don't overwrite __init__, use __singletoninit__
    instead
    
    @warning: Don't use UniqueRooms in QuestDungeons. Strange
    behavior will occur 
    """

    singletonready = Boolean()
    
    def __new__(cls, *args):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance
 
 
    def __init__(self):
        if not self.singletonready:
            self.__singletoninit__()
            self.singletonready = True
 
        
    def __singletoninit__ (self):
        Room.__init__ (self)
