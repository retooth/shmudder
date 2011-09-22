#!/usr/bin/python

from basic.exceptions import CharacterNotFound

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


# network layer
#################################################

from engine.ormapping import Store
from basic.exceptions import UnknownPlayer, BadPassword, UnknownPlayerType, PlayerExists
from hashlib import sha512

 
def login (handler, regex, arguments):
    
    s = Store()    
    loginstr = arguments[0]
    playeridtuple = s.cursor.execute("select id from user where _login = ?",\
                                     (loginstr,)).fetchone()
        
    if not playeridtuple :
        raise UnknownPlayer("")
        
    playerid = playeridtuple[0]
    player   = s.objects[playerid]
    
    handler.wannabe = player
    handler.context = type(handler).passwordcontext()


def password (handler, regex, arguments):
         
    password = arguments[0]
    
    # compare hashes
    wannabe = handler.wannabe
    pwhash  = wannabe.password
        
    if not sha512(password).hexdigest() == pwhash :
        raise BadPassword("")
        
    handler.wannabe.wakeup(handler)
        
        
def logout (player,regex,arguments):
    player.logout()


def register (handler,regex,arguments):
    handler.switchToRegisterHandler()


def chooseCharacter (handler, regex, arguments):

    keyword = arguments[0]
    playert = handler.callPlayerType(keyword)
        
    if not playert :
        raise UnknownPlayerType("")
        
    handler.emergeWannabe(playert)
    handler.nextContext()
        

def showCharacterChoiceInfo (handler, regex, arguments):

    keyword = arguments[0]
    playert = handler.callPlayerType(keyword)
    
    if not playert :
        raise UnknownPlayerType("")
        
    playert.showTypeInfo(handler)


def chooseName (handler, regex, arguments):
  
    name = arguments[0]
    
    s = Store()
    playeridtuple = s.cursor.execute("select id from user where _login = ?",\
                                     (name,)).fetchone()
                                         
    if playeridtuple :
        raise PlayerExists("")
    
    handler.wannabe.login = name
    handler.wannabe.addSingularKeyword(name)
    handler.nextContext()


def choosePassword (handler, regex, arguments):        
    
    password = arguments[0]
    handler.wannabe.password = password
    handler.wannabe.choose(handler)


# player properties
#################################################

def showInfo (player,regex,arguments):
    player.showInfoScreen()


def showInventory (player, regex, arguments):   
    inventory = player.inventory
    inventory.showItems(actor=player)

# senses
#################################################

from basic.exceptions import DetailNotFound

def examine (player, regex, arguments):        
        
    room    = player.location    
    exstr   = arguments[0]
    details = room.callDetails(exstr)

    # TODO: recursive search, execute on items and characters
        
    if not details:
        raise DetailNotFound("")

    for detail in details:
        detail.examine(actor=player)



# enviroment
#################################################


def walk (player, regex, arguments):
            
    room      = player.location
    direction = arguments[0]
    room.leave(player, direction)


def showRoom (player, regex, arguments):        
    room = player.location
    room.showLong(player)


# fights
#################################################

def kill (player,regex,arguments):

    # get player's current room
    room = player.location
    
    data = arguments[0]
    
    # data contains the string representation
    # of the enemy. callCharacters returns
    # the corresponding character objects
    enemies = room.callCharacters(data)
        
    # if no character responded, raise exception
    if not enemies:
        raise CharacterNotFound("")
             
    for enemy in enemies:
        player.attack(enemy)
        
# items
#################################################
from basic.exceptions import ItemReceiverNotFound, ItemNotFound, UnsupportedUseAlias, UnsupportedUnuseAlias

def throwAway (player, regex, arguments):
        
    inv     = player.inventory
    itemstr = arguments[0]     
    items   = inv.callItems(itemstr)
        
        
    if not items :
        raise ItemNotFound("")
            
    for item in items:    
        item.throwAway(actor=player)


def take (player, regex, arguments):
    
    room    = player.location
    itemstr = arguments[0]
    items   = room.callItems(itemstr)
        
        
    if not items :
        raise ItemNotFound("")
            
    for item in items:    
        item.take(actor=player)


        
def giveTo (player, regex, arguments):
        
    itemstr   = arguments[0]
    receivstr = arguments[1]
        
    inv   = player.inventory     
    items = inv.callItems(itemstr)
        
        
    if not items :
        raise ItemNotFound("")
        
    room = player.location
        
    receivers = room.callCharacters(receivstr)
        
    if not receivers:
        raise ItemReceiverNotFound("")
        
    # this approach makes sure, that if a bunch
    # of items should be transfered to a bunch of
    # players, every player gets an equal amount
    # of items
        
    # go until list of items is empty
    while items != [] :
            
        # give every player his/her item
        for r in receivers :
                
            # bad luck, no more items were mentioned
            if items == [] :
                break
                
            # take first item in list and give
            # it to current receiver
            item = items.pop(0)
                
            item.giveTo(actor=player,receiver=r)

     
def putInto (player,regex,arguments):
    
    itemstr = arguments[0]
    binstr  = arguments[1]
        
    inv   = player.inventory     
    items = inv.callItems(itemstr)
        
    if not items :
        raise ItemNotFound("")
            
    bins  = player.location.callItems(binstr)
    bins += player.inventory.callItems(binstr)
        
    if not bins:
        raise ItemNotFound("")
             
    # (see giveTo)    
    while items != [] :
            
        for b in bins :
                
            if items == [] :
                break
                
            item = items.pop(0)    
            item.putInto(player,b)

        
def takeOut (player,regex,arguments):
        
    itemstr = arguments[0]
    
    inv  = player.inventory
    room = player.room
    
    items =  inv.callAllItems(itemstr)
    items += room.callAllItems(itemstr)
        
    if not items:
        raise ItemNotFound("")
        
    for item in items:
        item.takeOut(actor=player)
        


def use (player, regex, arguments):
        
    inv     = player.inventory
    itemstr = arguments[0]     
    items   = inv.callItems(itemstr)
        
    if not items :
        raise ItemNotFound("")
    
    supported = []
    for item in items:
        if item.supportsUseAlias(regex):
            supported.append(item)
    
    if not supported :
        raise UnsupportedUseAlias("")
    
    for item in supported:    
        item.use(actor=player)
                

def unuse (player, regex, arguments):
        
    inv     = player.inventory
    itemstr = arguments[0]     
    items   = inv.callItems(itemstr)
        
    if not items :
        raise ItemNotFound("")
    
    supported = []
    for item in items:
        if item.supportsUnuseAlias(regex):
            supported.append(item)
    
    if not supported :
        raise UnsupportedUnuseAlias("")
    
    for item in supported:    
        item.unuse(actor=player)
                
