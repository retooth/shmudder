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

from engine.ormapping import Persistent, BackRef, String, Reference, Boolean
from abstract.causality import SignalListener, Signal
from basic.rooms import Room


class Dungeon (Persistent):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    A Dungeon is a collection of rooms. For additional uses
    of dungeons, see QuestDungeon
    """

    rooms = BackRef(Room,"dungeon")
    
    def __init__ (self):
        Persistent.__init__(self)
    
    
    def getClone(self, identifier):
        return self
    
    
    def addRoom (self, room):
        """ Adds a new room to the dungeon """
        room.dungeon = self
    
    
    def removeRoom (self, room):
        """ Removes a room from the dungeon"""
        room.dungeon = None
    
    
    def getCharacters (self):
        characters = []
        for room in self.rooms:
            characters += room.characters
        return characters
    
    characters = property(fget=getCharacters, \
                          doc="A list of all characters in this dungeon")


class QuestTask (Persistent):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Saves a pair (name,complete) and links it to
    a QuestCompletionListener
    """
    
    name  = String()
    complete = Boolean()
    completionlistener = Reference()
    
    def __init__ (self, listener, name):
        Persistent.__init__(self)
        self.name = name
        self.complete = False
        self.completionlistener = listener


class TaskCompletionSignal (Signal):
    
    """ 
    @author: Fabian Vallon
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Emit this type of signal in ANY QuestDungeon room and the
    appropriate task will be flagged as complete
    """
    
    def __init__ (self, taskname):
        Signal.__init__(self)
        self.taskname = taskname


class QuestCompletionListener (SignalListener):

    """ 
    @author: Fabian Vallon
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Global Listener for QuestDungeons. Features a list
    of completed tasks. Don't try to manipulate this
    class during the game. Use the addTask method of
    the QuestDungeon instance and TaskCompletionSignals
    for this. 
    """    
    
    dungeon  = Reference()
    tasks    = BackRef(QuestTask,"completionlistener")
    complete = Boolean()
    
    def __init__ (self, dungeon):
        SignalListener.__init__(self)
        self.dungeon = dungeon
        self.complete = False
    
    
    def addTask (self, name):
        task = QuestTask(self, name)
    
        
    def signalReceived (self, signal):     
        if self.complete:
            return
        if not isinstance(signal, TaskCompletionSignal):
            return
        name = signal.taskname
        for task in self.tasks:
            if task.name == name :
                task.complete = True
        self.checkCompletion()
         
         
    def checkCompletion (self):
        """ checks for completed tasks and invokes
        dungeons questComplete method if necessary """
        for t in self.tasks :
            if not t.complete:
                return
                break
        self.complete = True
        self.dungeon.questComplete()
            

class QuestDungeon (Dungeon):
    
    """ 
    @author: Fabian Vallon
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    QuestDungeons clone themselves for each player party.
    This way several parties can solve a quest at the
    same time 
    """    
    
    identifier = String()
    completionlistener = Reference()
    
    def __init__ (self):
        Dungeon.__init__(self)
        self.completionlistener = QuestCompletionListener(self)
    
    
    def getClone(self, identifier):
        """ Returns clone for identifier """
        dungeons = self.getAllInstances()
        for d in dungeons:
            if d.identifier == identifier:
                return d
                break
        newd = self.__class__()
        newd.identifier = identifier
        return newd
    
    
    def addRoom (self, room):
        """ adds room to dungeon and adds 
        QuestCompletionListener to room"""
        Dungeon.addRoom(self, room)
        room.addListener(self.completionlistener)
    
    
    def addTask (self, name):
        """ Adds a task to QuestDungeon. Use
        TaskCompletionSignal to flag it as solved """
        self.completionlistener.addTask(name)
    
    
    def questComplete(self):
        """[Event method] Gets invoked if quest is complete"""
        pass