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

from engine.ormapping import Persistent, PickleType, String
from abstract.exceptions import *

class Addressable (Persistent):
    
    # "What we cannot speak about we must pass over in silence" (Wittgenstein)
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Makes an object answer to a string representation
    """

    skeywords = PickleType()
    pkeywords = PickleType()

    def __init__ (self):
        Persistent.__init__(self)
        self.skeywords = []
        self.pkeywords = []
    
        
    def addSingularKeyword (self,keyword):
        """ Adds a singular keyword """
        self.skeywords = self.skeywords + [keyword]


    def addPluralKeyword (self,keyword):
        """ Adds a plural keyword """
        self.pkeywords = self.pkeywords + [keyword]
    
    
    def call (self,keyword):
        """ 
        Responds to singular and plural nouns. 
        - Returns 0, if thing doesn't answer to the name of keyword
        - Returns 1, if thing is called AS SINGULAR by keyword
        - Returns 2, if thing is called AS PLURAL by keyword
        @rtype: int 
        """
        if keyword in self.skeywords:
            return 1
        if keyword in self.pkeywords:
            return 2
        return 0


class AddressableCollection (Persistent):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Template for Collections, that include Addressable objects
    """
    
    def callCollectionItems (self, keyword, collection):
        """ 
        Gets all items in collection, that respond to keyword. Returns
        only a one-item list, if keyword was singular
        
        @param collection: list of addressable things
         
        @rtype: list<Addressable>
        """
        found = []
        for thing in collection:
            
            # forward call
            response = thing.call(keyword)
            
            # handle response as specified in Addressable.call(key)
            # 1 means: thing found and it was a singular noun
            
            if response == 1:
                found.append(thing)
                # break - no further stuff was mentioned
                break
            
            # 2 means: thing found and it was a plural noun
            elif response == 2:
                
                found.append(thing)
                # --- no break here --- just proceed and look 
                # if anything else responds
                
        return found


class Perceivable (Addressable):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Implements player actions for visual nature,
    smell, surface feeling and sound
    """
    
    shortdescription = String()
    longdescription  = String()
    odor             = String()
    feeling          = String()
    sound            = String()
    
    def __init__ (self):
        Addressable.__init__(self)
        self.shortdescription = ''
        self.longdescription  = ''
        self.odor = ''
        self.feeling = ''
        self.sound = ''
    
        
    def showShort (self, actor):
        if self.shortdescription:
            actor.receiveMessage(self.shortdescription)
            return
        raise Invisible("")


    def showLong (self, actor):
        if self.longdescription:
            actor.receiveMessage(self.longdescription)
            return
        raise Invisible("")


    def smell (self, actor):
        if self.odor:
            actor.receiveMessage(self.odor)
            return
        raise NoOdor("")

        
    def touch (self, actor):
        if self.feeling:
            actor.receiveMessage(self.feeling)
            return
        raise NoFeeling ("")

            
    def listen (self, actor):
        if self.sound:
            actor.receiveMessage(self.sound)
            return
        raise NoSound("")
            

