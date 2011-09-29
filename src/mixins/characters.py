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

from basic.tasks import Fights
from basic.exceptions import CantAttackThisCharacter
from mixins.fights import FightFilter

class MilitantCharacter (object):
    
    """ This class extends the Character class by the ability to fight """
    
    def __init__ (self):
        self.fights = Fights(self)
        self.fights.start(1.0)
    
    
    def __postload__ (self):
        self.fights = Fights(self)
        self.fights.start(1.0)
    
    
    def getOpponents (self):
        return self.fights.opponents
    
    opponents = property(getOpponents)


    def attack (self,opponent):    
        """ this method will initiate a fight. """
        if not ("fights" in dir(opponent) and \
                "fights" in dir(self)) :
            raise CantAttackThisCharacter("") 
 
        self.fights.addEnemy(opponent)
        opponent.fights.addEnemy(self)    
        
    
    def inflictDefaultDamage (self,opponent):
        """ 
        interface specification. game designer has to overwrite this.
        fallback method for fights. if character doesn't carry any weapon
        this method will inflict the damage
        @raise NotImplementedError: always
        """
        raise NotImplementedError(str(type(self)) + ": Lack of inflictDefaultDamage method")


    def inflictDamage (self,opponent):
        """
        this method will be called in fights. it will forward the
        call to player's weapons or to the inflictDefaultDamage method
        if player doesn't carry any weapon
        @param opponent: opponent in fight 
        """        
        weaponfound = False
        
        for item in self.inventory.items:
        
            #if it is a weapon..
            if "inflictDamage" in dir(item) and item.isInUse():
                item.inflictDamage(self,opponent)
                weaponfound = True
        
        if not weaponfound :    
            # otherwise call default method
            return self.inflictDefaultDamage(opponent)
    
    
    def sufferSimpleDamage (self,actor,value,constitutiontype):
        """
        will substract <value> points from player's constitution
        
        @param value: damage value (int)
        @param constitutiontype: type of constitution
        """
        for filter in self.fightfilters:
            value = filter.filter(self,actor,value)
        
        for c in self.constitution:
            if isinstance(c,constitutiontype):
                c.impair(actor,value)
        
    
    def getFightFilters (self):
        f = []
        for item in self.inventory.items :
            if isinstance(item,FightFilter) and item.inuse :
                f.append(item) 
        return f
          
    fightfilters = property(getFightFilters)
    
    
    def die (self) :
        
        """resets fights (additional events should be added)"""
        self.fights.reset()
        

    def clearInventory (self):
        
        """
        triggers the lose method for every item in inventory
        """
        
        for i in self.inventory.items :
            i.lose(actor=self)
