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

from abstract.perception import Adressable, Perceivable, AdressableCollection
from basic.details import DetailCollection
from collections import defaultdict
from engine.ormapping import Reference, BackRef, PickleType, Boolean
from mixins.misc import Groupable
from basic.exceptions import NotABin, UnsuitableBin, ImpossibleAction, ItemNotInUse, UnusableItem

class Item (DetailCollection,
            Adressable,
            Perceivable):

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


    __class_table__ = "Item"
    collection = Reference()

    def __init__(self):
        DetailCollection.__init__(self)
        Adressable.__init__(self)
        Perceivable.__init__(self)
        self.collection = None
    
    def use (self):
        raise UnusableItem("")
    
    def isInUse (self):
        """ [internal] Just a default to avoid type checking
        Returns always False
        """
        return False

    def take (self,actor):

        """ [player action] Moves item from room to inventory """

        room = actor.location
        inv  = actor.inventory
        room.removeItem(self)
        inv.addItem(self)

    def throwAway (self,actor):

        """ [player action] Moves item from inventory to room """
    
        # if an item is in use, it should be unused first
        if self.isInUse() :
            self.unuse(actor)
            
        room = actor.location
        inv  = actor.inventory
        inv.removeItem(self)
        room.addItem(self)
        

    def giveTo (self,actor,receiver):

        """ [player action] Moves item from inventory to another inventory """

        # if an item is in use, it should be unused first
        if self.isInUse() :
            self.unuse(actor)

        inv  = actor.inventory
        inv2 = receiver.inventory
        inv.removeItem(self)
        inv2.addItem(self)
        
    def putInto (self,actor,container):

        """ [player action] Puts item into container """

        if not isinstance(container,ItemCollection):
            raise NotABin("")

        # if an item is in use, it should be unused first
        if self.isInUse() :
            self.unuse(actor)
      
        self.collection.removeItem(self)
        container.addItem(self)

        
    def takeOut (self,actor):

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
        


class ItemCollection (AdressableCollection):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1

    A simple collection for items. Supports groupable items
    """

    unsorteditems = BackRef(Item,"collection")

    def __init__(self):
        AdressableCollection.__init__(self)

    def addItem (self, i):

        """ adds item to collection """
        i.collection = self


    def removeItem (self, i):

        """ removes item from collection """
        i.collection = None

    def getItems (self):
        
        unsorted = self.unsorteditems
        
        used = []
        unused = []
        for ui in unsorted :
            if ui.isInUse():
                used.append(ui)
            else :
                unused.append(ui)
                
        return unused + used
    
    items = property(fget=getItems,doc="sorted items (unused first)")


    def getAllItems (self):
        
        all = []
        q   = [self]
        
        while q :
            current = q.pop(0)
            for i in current.items:
                all.append(i)
                if isinstance(i,ItemCollection):
                    q.append(i)
        
        return all

    allitems = property(fget = getAllItems,\
                        doc  = "Searchs recursively for items in collection")

    def callItems (self,keyword):
        
        """ 
        Calls every item in collection by keyword and
        returns responding items
        
        @rtype: list<Item>
        """
        
        items = self.items
        items = self.callCollectionItems(keyword,items)
        return items
    
    def showItems (self,actor):
    
        """ 
        Shows every item in collection, groups groupable items
        """
                
        # initialize a counting dictionary for
        # groupable items
        count = defaultdict(int)
        
        items = self.items
        
        for i in items:
            
            # if item is groupable ..
            if isinstance(i,Groupable) :
                count[type(i)] += 1    
            else :
                # .. otherwise proceed normally
                i.showShort(actor)
        
        # group groupable items
        for itemtype in count.keys() :
            
            amount = count[itemtype]
            itemtype.showGroup(actor,amount)




class ChooseyItemCollection (ItemCollection):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1

    Excludes certain items from being added
    """
    
    def __init__ (self):
        ItemCollection.__init__(self)
    
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
    
    __class_table__ = "ReusableItem"
    
    necessaryslots = PickleType()
    inuse          = Boolean()
    
    def __init__ (self):
        Item.__init__(self)
        self.necessaryslots = []
        self.inuse = False
    
    def addBodyRequirement (self,keyword):
        
        """
        adds a body requirement for this item (keyword should
        be str and match a body part)
        """
        
        self.necessaryslots = self.necessaryslots + [keyword]

    def use (self, actor):
        
        """ 
        [player action] Uses the item (if possible) """
        
        for slot in self.necessaryslots:
        
            slots = actor.callBodyParts(slot)
            slots = filter(lambda x: x.item != self,slots)
            if not slots :
                self.unuse(actor)
                raise ImpossibleAction("")
            
            bp = slots[0]
            
            if bp.item :
                bp.item.unuse(actor)
                
            bp.item = self
            
        self.inuse = True

            
    def unuse (self, actor):
        
        """ [player action] Unuses the item """

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
    
    def supportsUseAlias (self,regex):
        """ Define here, if item supports regex as an usage
        alias. Returns False as default 
        @rtype: bool"""
        return False
    
    def supportsUnuseAlias (self,regex):
        """ Define here, if item supports regex as an unuse
        alias. Returns False as default 
        @rtype: bool"""
        return False


# TODO:
class Clothing (ReusableItem):
    pass