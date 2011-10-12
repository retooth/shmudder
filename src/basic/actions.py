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


# network layer
#################################################

from engine.ormapping import Store
from basic.exceptions import UnknownPlayer, BadPassword
from basic.exceptions import UnknownPlayerType, PlayerExists
from hashlib import sha512

 
def login (handler, regex, arguments):
    """ gets invoked after player typed login name """
    s = Store()    
    loginstr = arguments[0]
    playeridtuple = s.cursor.execute("select id from user where _login = ?", \
                                     (loginstr, )).fetchone()
        
    if not playeridtuple :
        raise UnknownPlayer("")
        
    playerid = playeridtuple[0]
    player   = s.objects[playerid]
    
    handler.wannabe = player
    handler.context = type(handler).passwordcontext()


def password (handler, regex, arguments):
    """ gets invoked after player typed password """
    password = arguments[0]
    
    # compare hashes
    wannabe = handler.wannabe
    pwhash  = wannabe.password
        
    if not sha512(password).hexdigest() == pwhash :
        raise BadPassword("")
        
    handler.wannabe.wakeup(handler)
        
        
def logout (player, regex, arguments):
    """ logs player out """
    player.logout()


def register (handler, regex, arguments):
    """ starts register process """
    handler.switchToRegisterHandler()


def chooseCharacter (handler, regex, arguments):
    """ chooses character type in register process """
    keyword = arguments[0]
    playert = handler.callPlayerType(keyword)
        
    if not playert :
        raise UnknownPlayerType("")
        
    handler.emergeWannabe(playert)
    handler.nextContext()
        

def showCharacterChoiceInfo (handler, regex, arguments):
    """ 
    shows an info screen about a character type 
    in register process 
    """
    keyword = arguments[0]
    playert = handler.callPlayerType(keyword)
    
    if not playert :
        raise UnknownPlayerType("")
        
    playert.showTypeInfo(handler)


def chooseName (handler, regex, arguments):
    """ determines the player's name in register process """
    name = arguments[0]
    
    s = Store()
    playeridtuple = s.cursor.execute("select id from user where _login = ?", \
                                     (name, )).fetchone()
                                         
    if playeridtuple :
        raise PlayerExists("")
    
    handler.wannabe.login = name
    handler.wannabe.addSingularKeyword(name)
    handler.nextContext()


def choosePassword (handler, regex, arguments):        
    """ chooses player's password in register process """
    password = arguments[0]
    handler.wannabe.password = password
    handler.wannabe.choose(handler)


# player properties
#################################################

def showInfo (player, regex, arguments):
    """ forwarder to player's showInfoScreen method """
    player.showInfoScreen()


def showInventory (player, regex, arguments):
    """ invokes showItems on player's inventory """   
    inventory = player.inventory
    inventory.showItems(actor=player)

# senses
#################################################

from basic.exceptions import DetailNotFound

def examine (player, regex, arguments):        
    """ examines something in the room or inventory """
    room    = player.location    
    exstr   = arguments[0]
    details = room.callDetails(exstr)
    items   = player.inventory.callItems(exstr)
    chars   = room.callCharacters(exstr)
    
    if not (details or items) :
        raise DetailNotFound("")

    all = details + items + chars

    for obj in all:
        obj.showLong(player)    

def smell (player, regex, arguments):        
    """ smells something in room or inventory """
    room    = player.location    
    exstr   = arguments[0]
    details = room.callDetails(exstr)
    items   = player.inventory.callItems(exstr)
    chars   = room.callCharacters(exstr)
    
    if not (details or items) :
        raise DetailNotFound("")

    all = details + items + chars

    for obj in all:
        obj.smell(player)    

def listen (player, regex, arguments):        
    """ listens to something in room or inventory """
    room    = player.location    
    exstr   = arguments[0]
    details = room.callDetails(exstr)
    items   = player.inventory.callItems(exstr)
    chars   = room.callCharacters(exstr)
    
    if not (details or items) :
        raise DetailNotFound("")

    all = details + items + chars

    for obj in all:
        obj.listen(player)    

def touch (player, regex, arguments):        
    """ touches something in room or inventory """
    room    = player.location    
    exstr   = arguments[0]
    details = room.callDetails(exstr)
    items   = player.inventory.callItems(exstr)
    chars   = room.callCharacters(exstr)
    
    if not (details or items) :
        raise DetailNotFound("")

    all = details + items + chars

    for obj in all:
        obj.touch(player)    


# enviroment
#################################################


def walk (player, regex, arguments):
    """ changes current room """
    room      = player.location
    direction = arguments[0]
    room.leave(player, direction)


def showRoom (player, regex, arguments): 
    """ shows room description """       
    room = player.location
    room.showLong(player)


# fights
#################################################

from basic.exceptions import CharacterNotFound

def kill (player, regex, arguments):
    """ kills another player """
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
from basic.exceptions import ItemReceiverNotFound, ItemNotFound 
from basic.exceptions import UnsupportedUseAlias, UnsupportedUnuseAlias

def throwAway (player, regex, arguments):
    """ throws item away """
    inv     = player.inventory
    itemstr = arguments[0]     
    items   = inv.callItems(itemstr)
        
        
    if not items :
        raise ItemNotFound("")
            
    for item in items:    
        item.throwAway(actor=player)


def take (player, regex, arguments):
    """ takes item """
    room    = player.location
    itemstr = arguments[0]
    items   = room.callItems(itemstr)
        
        
    if not items :
        raise ItemNotFound("")
            
    for item in items:    
        item.take(actor=player)


        
def giveTo (player, regex, arguments):
    """ gives item to another character """
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
                
            item.giveTo(player, r)

     
def putInto (player, regex, arguments):
    """ puts item in another item """
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
            item.putInto(player, b)

        
def takeOut (player, regex, arguments):
    """ takes item out of another item """
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
    """ uses item """
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
    """ puts item back into inventory """
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
                
