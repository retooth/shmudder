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

from basic.items import ReusableItem

class Weapon (ReusableItem):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Interface specification for weapons
    """
    
    def __init__ (self):
        ReusableItem.__init__(self)
    
    
    def inflictDamage (self, actor, opponent): 
        """ should implement damage in fights """
        clsn = self.__class__.__name__
        raise NotImplementedError(clsn + " should have a inflictDamage method")


class AmmoDrivenWeapon (Weapon):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Base class for weapons, which need ammunition
    """
    
    def __init__ (self):
        Weapon.__init__(self)
        self.nextammo = None
    
    
    def __postload__ (self):
        self.nextammo = None


    def isSuitableAmmo (self, ammo):
        """ should return bool, if ammo a is suitable """
        clsn = self.__class__.__name__
        raise NotImplementedError(clsn+": Lack of isSuitableAmmo method")


    def outOfAmmo (self, actor):
        """ [event method] gets invoked, if no ammo
        is in the inventory """
        pass

    
    def ammoNotPresent (self, actor):
        """ [event method] gets invoked, if ammo is not
        in a collection used by the player """
        pass


    def inflictDamage(self, actor, opponent):

        if not self.nextammo:

            inv   = actor.inventory
            items = inv.allitems        
            
            ammo  = filter(self.isSuitableAmmo, items)
            
            if not ammo:
                self.outOfAmmo(actor)
                return
    
            present = []                
            for a in ammo :
                if a.collection is not inv and \
                   a.collection.isInUse():    
                    present.append(a)
            
            if not present:
                self.ammoNotPresent(actor)
                self.nextammo = ammo[0]
                return
        
            ammo = ammo[0]
            
        else :
            
            ammo = self.nextammo
            self.nextammo = None
            
        if ammo.collection is not actor.inventory :
            ammo.takeOut(actor)
            
        ammo.inflictDamage(actor, opponent)
            