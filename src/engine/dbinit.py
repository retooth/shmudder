#!/usr/bin/python

from engine.locals import *

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


def createBaseTables ():

    """
    Creates all base tables
    """

    Persistent.createTable()

    M2M_EnviromentEmitter.createTable()
    M2M_EnviromentListener.createTable()
    
    Improvable.createTable()
    GradualImprovable.createTable()
    Attribute.createTable()
    AttributeCollection.createTable()
    
    Adressable.createTable()
    Perceivable.createTable()
    
    Constitution.createTable()
    
    
    BodyPart.createTable()
    Character.createTable()
    Party.createTable()
    Player.createTable()
    
    Detail.createTable()
    
    Dungeon.createTable()
    
    Item.createTable()
    ReusableItem.createTable()
    Exit.createTable()
    Room.createTable()
    DefaultRoom.createTable()
    
    LightSource.createTable()
    LightIntensityListener.createTable()
    IlluminatedRoom.createTable()
    
    #Aura.createTable()
    #AuraCollection.createTable()
    
    #Communicator.createTable()
    User.createTable()
    
