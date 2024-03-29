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

from abstract.perception import DetailedPerceivable, callAdressables
from collections import defaultdict
from engine.ormapping import Reference, BackRef, PickleType
from engine.ormapping import Boolean, Integer
from mixins.misc import Groupable
from basic.exceptions import NotABin, UnsuitableBin, ImpossibleAction
from basic.exceptions import UneatableItem, UnwearableItem, UndrinkableItem 
from basic.exceptions import ItemNotInUse, UnusableItem

class Item (DetailedPerceivable):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1

    Basic Item class, that supports the following actions
    - take / throwaway
    - putInto / takeOutOf
    - giveTo
    - loose (will be triggered by Inventory.clear())
    """

    collection = Reference()
    weight     = Integer()

    def __init__ (self):
        DetailedPerceivable.__init__(self)
        self.collection = None
        self.weight = 0
        self.explicit = True


    def getLocation (self):
        if not self.collection:
            return
        return self.collection.location
    
    location = property(getLocation)
    
    
    def locationChanged (self, old, new, keyword):
        """ [event method] gets invoked if item is carried
        from one room to another """
        pass
    
    
    def isInUse (self):
        """ [internal] Just a default to avoid type checking
        Returns always False
        """
        return False


    def take (self, actor):
        """ [player action] Moves item from room to inventory """
        room = actor.location
        inv  = actor.inventory
        room.removeItem(self)
        inv.addItem(self)


    def throwAway (self, actor):
        """ [player action] Moves item from inventory to room """
        # if an item is in use, it should be unused first
        if self.isInUse() :
            self.putAway(actor)
            
        room = actor.location
        inv  = actor.inventory
        inv.removeItem(self)
        room.addItem(self)
        

    def giveTo (self, actor, receiver):

        """ [player action] Moves item from inventory to another inventory """

        # if an item is in use, it should be put away first
        if self.isInUse() :
            self.putAway(actor)

        inv  = actor.inventory
        inv2 = receiver.inventory
        inv.removeItem(self)
        inv2.addItem(self)

        
    def putInto (self, actor, container):
        """ [player action] Puts item into container """
        # TODO: Check, if bag / or dynamic typecheck
        if not isinstance(container, ItemCollection):
            raise NotABin("")

        # if an item is in use, it should be put away first
        if self.isInUse() :
            self.putAway(actor)
      
        self.collection.removeItem(self)
        container.addItem(self)

        
    def takeOut (self, actor):
        """ [player action] Takes item out of container """
        actor.inventory.addItem(self)


    def loose (self, actor):
        """ [player action] Looses item """
        # free bodyparts (suppress unuse messages)
        bodyparts = actor.bodyparts
        for bp in bodyparts:
            if bp.item == self :
                bp.item = None
        self.inuse = False
        
        room = actor.location
        room.addItem(self)
        

class ItemCollection (object):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1

    A simple collection for items. Supports groupable items
    Volatile mixin
    """

    unsorteditems = BackRef(Item,"collection")

    def addItem (self, i):
        """ adds item to collection """
        i.collection = self


    def removeItem (self, i):
        """ removes item from collection """
        i.collection = None


    def getItems (self):        
        used = []
        unused = []
        for uitem in self.unsorteditems :
            if uitem.isInUse():
                used.append(uitem)
            else :
                unused.append(uitem)
                
        return unused + used
    
    items = property(fget = getItems, \
                     doc  = "sorted items (unused first)")


    def getAllItems (self):
        all = []
        queue   = [self]
        while queue :
            current = queue.pop(0)
            for item in current.items:
                all.append(item)
                if isinstance(item, ItemCollection):
                    queue.append(item)
        
        return all

    allitems = property(fget = getAllItems, \
                        doc  = "Searchs recursively for items in collection")


    def callItems (self, keyword):        
        """ 
        Calls every item in collection by keyword and
        returns responding items
        @rtype: list<Item>
        """
        items = callAdressables(keyword, self.items)
        return items

    
    def showItems (self, actor):
        """ Shows every item in collection, groups groupable items"""
        # initialize a counting dictionary for
        # groupable items
        count = defaultdict(int)
        
        items = self.items
        
        for i in items:
            
            # if item is groupable ..
            if isinstance(i, Groupable) :
                count[type(i)] += 1    
            else :
                # .. otherwise proceed normally
                i.showShort(actor)
        
        # group groupable items
        for itemtype in count.keys() :
            
            amount = count[itemtype]
            itemtype.showGroup(actor, amount)
            

class ChooseyItemCollection (ItemCollection):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1

    Excludes certain items from being added
    """
    
    def permits (self, i):
        """Should return bool, if i is permitted in this collection"""
        raise NotImplementedError("ChooseyItemCollection must have a permits method")
    
    def addItem (self, i):        
        if not self.permits(i):
            raise UnsuitableBin("")
        ItemCollection.addItem(self, i)


class ReusableItem (Item):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1

    Implements player action methods for item usage
    """
        
    necessaryslots = PickleType()
    inuse          = Boolean()
    
    def __init__ (self):
        Item.__init__(self)
        self.necessaryslots = []
        self.inuse = False
    
    
    def addBodyRequirement (self, keyword):    
        """
        adds a body requirement for this item (keyword should
        be str and match a body part)
        """
        self.necessaryslots = self.necessaryslots + [keyword]


    def use (self, actor):        
        """ [player action] Uses the item (if possible) """
        for slot in self.necessaryslots:
        
            slots = actor.callBodyParts(slot)
            slots = filter(lambda x: x.item != self, slots)
            if not slots :
                self.putAway(actor)
                raise ImpossibleAction("")
            
            bp = slots[0]
            
            if bp.item :
                bp.item.unuse(actor)
                
            bp.item = self
            
        self.inuse = True

            
    def putAway (self, actor):
        
        """ [player action] puts the item back into inventory """

        if not self.isInUse() :
            raise ItemNotInUse("")
        
        # free bodyparts
        bodyparts = actor.bodyparts
        
        for bp in bodyparts:
            if bp.item == self :
                bp.item = None
                
        self.inuse = False


    def isInUse (self):        
        """ returns boolean, if item is in use"""
        return self.inuse


class Clothing (ReusableItem):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1

    Implements putOn and takeOff methods
    """
    
    def putOn (self, actor):
        self.use(actor)
    
    
    def takeOff (self, actor):
        self.putAway(actor)


class Weapon (ReusableItem):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Interface specification for weapons. Implements
    draw method
    """
    
    def draw (self, actor):
        self.use(actor)
    
    
    def inflictDamage (self, actor, opponent): 
        """ should implement damage in fights """
        clsn = self.__class__.__name__
        raise NotImplementedError(clsn + " should have a inflictDamage method")


class Food (ReusableItem):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Implements eat method
    """
    
    leftover = Integer()
    
    def __init__ (self):
        ReusableItem.__init__(self)
        self.leftover = 1
        """ gets decremented after every bite. if 0, item will be
        deleted. 1 by default """
        
        
    def eat (self, actor):
        self.use(actor)
        self.leftover = self.leftover - 1
        if not self.leftover:
            del self
            self.foodFinished (self,actor)
            return
        self.putAway(actor)
    
    
    def foodFinished (self, actor):
        """ [event method] gets called if leftover hits 0 """
        pass
    

class Beverage (ReusableItem):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Implements drink method
    """
    
    leftover = Integer()
    
    def __init__ (self):
        ReusableItem.__init__(self)
        self.leftover = 1
        """ gets decremented after every bite. if 0, item will be
        deleted. 1 by default """
    
        
    def drink (self, actor):
        self.use(actor)
        self.leftover = self.leftover - 1
        if not self.leftover:
            del self
            self.beverageFinished (self,actor)
            return
        self.putAway(actor)
    
    
    def beverageFinished (self, actor):
        """ [event method] gets called if leftover hits 0 """
        pass