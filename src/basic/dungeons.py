#!/usr/bin/python

from engine.ormapping import Persistent, BackRef
from basic.rooms import Room

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
    
    def addRoom (self,newr):
        """ Adds a new room to the dungeon """
        newr.dungeon = self
    
    def removeRoom (self,r):
        """ Removes a room from the dungeon"""
        r.dungeon = None
    
    def getCharacters (self):
        characters = []
        for r in self.rooms:
            characters += r.characters
        return characters
    
    characters = property(fget=getCharacters,doc="A list of all characters in this dungeon")
