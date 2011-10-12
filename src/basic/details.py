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

from abstract.perception import Perceivable, callAdressables
from engine.ormapping import Reference, BackRef, Boolean

class Detail (Perceivable):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Details are non-portable objects made to provide
    a better description of things in your MUD
    """

    collection = Reference()
    explicit   = Boolean()
    
    def __init__ (self):
        Perceivable.__init__(self)
        self.explicit = False
        """ Set this to True, if you want your Detail
        explicitely listed in room descriptions.
        (Don't forget to implement showShort)"""
        
    def getLocation (self):
        if not self.collection:
            return
        return self.collection.location
    
    location = property(getLocation)