#!/usr/bin/python

from twisted.internet.task import LoopingCall

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


class Fights (LoopingCall):
    
    
    def __init__ (self,fighter):
        LoopingCall.__init__(self, self.run)
        self.fighter = fighter
        self.fqueue = []    
    
    
    def getOpponents(self):
        return self.fqueue
    
    opponents = property(getOpponents)
    
    
    def addEnemy (self,enemy):
        self.fqueue.append(enemy)
    
    
    def removeEnemy (self,enemy):
        self.fqueue.remove(enemy)
    
    
    def reset (self):
            
        for enemy in self.opponents:
            enemy.fights.removeEnemy(self.fighter)
    
        self.fqueue = []
    
    
    def run (self):
        
        room = self.fighter.location
        if not room :
            return 

        q    = self.opponents[:]
        temp = []

        while q != [] :

            current = q.pop(0)
            temp.append(current)
            
            if current in room :
                self.fighter.inflictDamage(current)
                break
        
        # don't change. it has to be that complicated.
        # (inflictDamage could alter fqueue and we would
        # falsely overwrite it with our cache)
        q = list(set(q + temp).intersection(self.opponents))
        self.fqueue = q
