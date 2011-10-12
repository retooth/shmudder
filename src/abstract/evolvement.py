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

from basic.exceptions import *
from engine.ormapping import Persistent, Integer, PickleType

class Improvable (Persistent):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Improvable provides a quality attribute (which is bounded
    above, if you want) and event methods, that are triggered
    by quality change
    
    @note: Don't use percentage to determine if something is
    perfect or broken (rounding errors can happen) Use the
    property isperfect and isbroken instead
    """
    
    quality    = Integer()
    maxquality = Integer()
    
    def __init__ (self):
        Persistent.__init__(self)
        self.quality = 0
        self.maxquality = 0


    def getPercentage (self):    
        qfloat = float(self.quality)
        if not self.maxquality :
            return
        mfloat = float(self.maxquality)
        return (qfloat/mfloat)*100

    percentage = property(fget = getPercentage, \
                          doc  = "Quality in percent" )


    def isPerfect (self):
        # shouldn't need the >, but maybe there is
        # some strange behavior
        if (self.maxquality and
        self.quality >= self.maxquality):
            return True
        return False
    
    isperfect = property(fget = isPerfect, \
                         doc  = "True if quality is perfect")


    def isBroken (self):
        if self.quality :
            return False
        return True

    isbroken = property(fget = isBroken, \
                        doc  = "True if quality is 0")


    def improve (self, actor, value):

        """
        [player action] Gains quality by value. Stops at maximum 
        and calls qualityMaximum() if necessary
        """

        quality = self.quality
        max = self.maxquality
        
        nq = min(quality+value, max)
        self.qualityChanged(actor, quality, nq)
        
        self.quality = nq

        if nq == max :
            return self.qualityMaximum(actor)


    def impair (self, actor, value):

        """ 
        [Player action] Decreases quality by value. Stops at 0 and calls 
        qualityMinimum() if necessary
        """

        quality = self.quality
        
        nq = max(quality-value, 0)
        self.qualityChanged(actor, quality, nq)
        
        self.quality = nq
        
        if not nq :
            self.qualityMinimum(actor)

    
    def qualityChanged (self, actor, old, new):
        
        """[Event method] Gets invoked on every improve/impair action
        @param old: quality before change
        @param new: new quality
        """
        
        pass
    
    
    def qualityMaximum (self, actor):
        
        """[Event method] Gets invoked, when quality is maximal
        after improve() has been called.
        """
        
        pass

    
    def qualityMinimum (self, actor):
        
        """[Event method] Gets invoked, when quality is 0
        after impair() has been called.
        """
        
        pass


class GradualImprovable (Improvable):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Extends the Improvable Class to a level attribute.
    This is mainly used in the player class
    """
    
    
    level      = Integer()
    levelstops = PickleType()
    
    def __init__ (self):
        Improvable.__init__(self)
        self.level = 0
        self.levelstops = {}
    
    
    def getMaxLevel (self):
        return max(self.levelstops.keys())
    
    maxlevel = property(fget = getMaxLevel, \
                        doc  = "The highest level defined in levelstops")


    def improve (self, actor, value):
        
        """
        [player action] Gains quality by value. Stops at maximum 
        and calls qualityMaximum() if necessary. Increases the
        level attribute according to levelstops 
        """
        
        Improvable.improve(self, actor, value)
        
        if self.level != self.maxlevel:
            
            currq = self.quality
            
            # quality necessary for next level
            nextq = self.levelstops[self.level + 1]
            
            if currq >= nextq :
                self.level += 1
                return self.levelRaised(actor)
      
        
    def levelRaised (self, actor):
        
        """[Event method] Gets invoked after improve() raised
        level.
        """
    
    
    def resetQuality (self):
        
        """For convenience. Resets quality to current level minimum """
        
        self.quality = self.levelstops[self.level]
        


