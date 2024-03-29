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

""" @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
        
    This module implements common methods, which players and NPCs share
    (like an inventory or the ability to inflict damage)
 """

from engine.ormapping import Persistent, Reference, BackRef
from engine.ormapping import Boolean, Integer, OneToOne
from abstract.perception import Addressable, DetailedPerceivable, callAdressables
from abstract.evolvement import GradualImprovable, Improvable
from basic.items import ItemCollection
from engine.user import User
from engine.client import GameHandler
from basic.exceptions import ImprovementNotAllowed


class BodyPart (Addressable):
    
    """ Body part class for reusable items """
    
    character = Reference()
    item      = Reference()
    
    def __init__ (self):
        Addressable.__init__(self)
        self.item = None


class Attribute (Improvable,
                 Addressable):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Attributes are 'semantic integers'. Typically an Attribute
    is something like Strenght or Stamina
    """
    
    collection = Reference()
    
    def __init__ (self):
        Improvable.__init__(self)
        Addressable.__init__(self)
        self.collection = None


    def improve (self, actor, value):
        """
        [player action] Gains attribute by value. Stops at maximum 
        and calls qualityMaximum() if necessary. Checks, if collection
        allows improvement at current time.
        """
        if self.collection.allowsimprovement:
            Improvable.improve(self, actor, value)
            self.collection.bonus = self.collection.bonus - 1 
        else :
            raise ImprovementNotAllowed("")


class AttributeCollection (Persistent):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    AttributeCollection provides a bonus attribute, that
    restricts the improvement of Attribute objects in the
    collection. This is a typical RPG behavior. If you want
    to disable this feature, set bonus to -1
    """

    attributes = BackRef(Attribute,"collection")
    bonus      = Integer()
    character  = Reference()

    def __init__ (self):
        Persistent.__init__(self)
        self.bonus = 0


    def allowsImprovement (self):        
        if self.bonus > 0 or self.bonus < 0:
            return True
        return False

    allowsimprovement = property(fget = allowsImprovement, \
                                 doc  = "True if bonus > 0 or feature disabled")
    
    
    def addAttribute (self, attribute):
        """ Adds an attribute to the collection """
        attribute.collection = self


    def removeAttribute (self, attribute):
        """Removes attribute attribute from the collection"""
        attribute.collection = None


    def callAttributes(self, keyword):
        """ 
        Calls every attribute in collection by keyword and
        returns responding attributes
        
        @param keyword: keyword, that should be checked 
        @rtype: list<Attribute>
        """
        attributes = callAdressables(keyword, self.attributes)
        return attributes


class Constitution (Improvable,
                    Addressable):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Constitution is similar to Attribute, yet a constitution
    object is linked to a character directly without being
    wrapped by a collection. 
    """
    
    character = Reference()
    
    def __init__ (self):
        Improvable.__init__(self)
        Addressable.__init__(self)
    
    def reset (self):
        """ 
        Simply sets quality to maxquality
        
        @Warning: Doesn't call qualityMaximum or
        qualityChanged
        """
        self.quality = self.maxquality
        

class VitalConstitution (Constitution):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    VitalConstitution overwrites the qualityMinimum method,
    and invokes the die() method on the linked character
    """
    
    def __init__ (self):
        Constitution.__init__ (self)
    
    def qualityMinimum (self, actor):
        """ [overwritten] invokes die method on character """
        self.character.die()


class Character (DetailedPerceivable):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Character class for players and NPCs
    """

    defaultlocation = Reference()
    location        = Reference()
    inventory       = Reference()
    communicator    = Reference()
    npcparty        = Reference()
    attributeset    = Reference()
    
    constitution      = BackRef(Constitution,"character")
    unsortedbodyparts = BackRef(BodyPart,"character")
      
    def __init__ (self):
        DetailedPerceivable.__init__(self)
        self.defaultlocation = None
        self.location = None
        self.communicator = None
        self.explicit = True
    
    def __initdefaults__ (self):
        """ Sets character attributes to basic defaults """
        self.inventory = Inventory()
        self.npcparty = Party()
        self.attributeset = AttributeCollection()
           
            
    def addBodyPart (self, bodypart):
        """ Adds a body part to the character """
        bodypart.character = self

    def removeBodyPart (self, bodypart):
        """ Removes a body part from the character """
        bodypart.character = None

    def getBodyParts (self):
        # this method will be called by reusable.use(). by standard
        # an item will be unused, when another item wants to take it's
        # place. this method will make sure, that free body parts will
        # be prefered, so an unuse will only happen, if it's necessary
        bplist = self.unsortedbodyparts
        
        # sort every body part into 'free' and 'used'
        freebp = []
        usedbp = []
        
        for bodypart in bplist :
        
            if bodypart.item == None :
                freebp.append(bodypart)
            else :
                usedbp.append(bodypart)
        
        # rebuild body parts list by two categories
        newlist = freebp + usedbp
        return newlist
        
    bodyparts = property(fget = getBodyParts, \
                         doc  = "Character's bodyparts (unused first)")


    def callBodyParts (self, keyword):
        return callAdressables(keyword, self.bodyparts)
    
    
    def addConstitution (self, character):        
        """Adds constitution to the character"""
        character.character = self


    def removeConstitution (self, character):
        """Removes constitution from the Character"""
        character.character = None

             
    def getConstitutionOfType (self, ctype):
        """
        will return constitution object for type <ctype>
        @rtype: constitution or None
        """
        clist = self.constitution
        for constitution in clist:
            if isinstance(constitution, ctype):
                return constitution
                break
        return None    


    def vanish (self):
        """ for convenience. removes character from room """
        p = self.location
        p.removeCharacter(self) 
 
    
    def resetConstitution (self):
        """ for convenience. resets every constitution to
        its maximum """
        for c in self.constitution :
            c.reset()


    def receiveMessage (self, message):
        
        """ standard method to avoid type checking
        in message allocation. Does nothing """
         
        pass    
        
    
    def locationChanged (self, old, new, keyword):
        """ [event method] gets invoked if characters
        leaves room """
        pass
    
    
        
class CharacterCollection (object):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    A collection made for Characters. Mainly used in
    Room Class, but in theory animal cages and similar
    objects are possible.
    Volatile Mixin
    """

    characters = BackRef(Character,"location")

    def addCharacter (self, character):
        """ Adds character to collection """
        character.location = self
        

    def removeCharacter (self, character):
        """ Removes character from the collection """
        character.location = None      


    def callCharacters (self, keyword):  
        """ 
        Calls every character in collection by keyword and
        returns responding characters
        @rtype: list<Character>
        """
        chars = callAdressables(keyword, self.characters)
        return chars
    
    
    def showCharacters (self, actor):
        """ Shows every character in collection """
        for c in self.characters :
            c.showShort(actor)
    
    
    def showOtherCharacters (self, actor):
        """ Shows every character in collection except actor """
        for c in self.characters :
            if c != actor :
                c.showShort(actor)



class Inventory (Persistent, ItemCollection):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    A very simple player inventory
    """

    character = OneToOne(Character,"inventory")

    def showItems (self, actor):
        actor.receiveMessage("-"*20)
        ItemCollection.showItems(self, actor)
        actor.receiveMessage("-"*20)
        
    
    def getLocation (self):
        return self.character.location
    
    location = property(getLocation)


class Player (GameHandler,
              User, 
              Character,
              GradualImprovable):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    """
        
    party = Reference()
    
    def __init__ (self):
        GameHandler.__init__(self)
        Character.__init__(self)
        GradualImprovable.__init__(self)
        User.__init__(self)
        self._context = None
    
    
    def __postload__ (self):
        self._context = None
    
    
    def __initdefaults__ (self):
        Character.__initdefaults__(self)
        self.party = Party()
    
    
    @staticmethod
    def showTypeInfo (handler):    
        """
        should show some info about the player type
        @raise NotImplementedError: always 
        """
        raise NotImplementedError("Lack of static showTypeInfo method")
     
     
    def showInfoScreen (self):    
        """
        should show an general info
        screen about the player.
        @raise NotImplementedError: always 
        """
        raise NotImplementedError ("Lack of showInfoScreen method")
        
        
    def choose (self, handler):
        """ [registerhandler action] gets invoked, if
        player creation process is done """
        handler.client.handler = self
        self.location = self.defaultlocation
    
    
    def wakeup (self, handler):    
        """ [loginhandler action] gets invoked, if
        player has successfully logged in """
        handler.client.handler = self
        self.location = self.lastlocation
        self.__contextinit__()
    
    
    def showShort (self, actor):
        name = self.skeywords[0]
        actor.receiveMessage(name)


    def logout (self):        
        """
        [player action] disconnects the client
        @warning: when overwriting, send messages
        BEFORE calling the supermethod
        """
        self.client.stopProducing()


class Party (Addressable, 
             CharacterCollection):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Parties are a crowds of players/npcs, who play and solve
    quests together
    """
    
    autofollow = Boolean()
    players    = BackRef(Player,'party')
    
    def __init__ (self):
        Addressable.__init__(self)
        CharacterCollection.__init__(self)
        self.autofollow = False

    
    def join (self, actor):
        """ [player action] player joins to the party"""
        self.addCharacter(actor)
        actor.party = self

        
    def leave (self, actor):
        """ [player action] player leaves to the party"""
        self.removeCharacter(actor)
        actor.party = None
        if not self.players:
            self.__delete__()
        

    def found (self, actor, keyword):
        """ [player action] party is founded (sets keyword)"""
        self.addSingularKeyword(keyword)
    
    
    def getIdentifier (self):
        """ returns an identifier for quest dungeons """ 
        logins = []
        for p in self.players:
            logins.append(p.login)
        s = sorted(logins)
        return "|".join(s)

    identifier = property(getIdentifier)
