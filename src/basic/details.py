#!/usr/bin/python

from abstract.perception import Adressable, Visible, AdressableCollection
from engine.ormapping import Reference, BackRef, Boolean

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


class Detail (Adressable,Visible):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Details are non-portable objects made to provide
    a better description of things in your MUD
    """

    
    __class_table__ = "Detail"
    collection = Reference()
    explicit   = Boolean()
    
    def __init__ (self):
        Adressable.__init__(self)
        
        self.explicit = False
        """ Set this to True, if you want your Detail
        explicitely listed in room descriptions.
        (Don't forget to implement showShort)"""
    
    def examine (self, actor):
        
        """ 
        [player action] Forwarding method for Visible.showLong()
        """
        
        self.showLong(actor)




class DetailCollection (AdressableCollection):

    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Class for every detailed thing
    """

    details = BackRef(Detail,"collection")

    def __init__ (self):
        AdressableCollection.__init__(self)

    def addDetail (self, detail):

        """ Adds a detail to the collection """
        detail.collection = self
        
    def removeDetail (self, detail):

        """Removes a detail from the collection"""
        detail.collection = None
        
    def callDetails (self, keyword):
        
        """ 
        calls every detail in collection by keyword and
        returns responding details
        
        @rtype: list<Detail>
        """
     
        details = self.details
        details = self.callCollectionItems(keyword, details)
        return details
    
    def showDetails (self, actor):
        
        """ [player action] shows every detail in collection """
        
        details = self.details[:]
        
        details = filter(lambda x : x.explicit,details)
        for d in details :
            d.showShort(actor)