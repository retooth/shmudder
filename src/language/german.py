#!/usr/bin/python

from language.universal import Context
from basic.actions import *
from basic.exceptions import *

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


class CharacterChoiceContext (Context):

    def __init__ (self):
        Context.__init__(self)
        
        self.addSemantics("waehle (.+)", chooseCharacter)
        self.addSemantics("info (.+)", showCharacterChoiceInfo)
        self.addExceptionHandling(UnknownAction, "Wie bitte ?")
        self.addExceptionHandling(UnknownPlayerType, "So einen Spielertyp gibt es nicht")

class LoginContext (Context):
    
    def __init__ (self):
        Context.__init__(self)
        self.addSemantics("neu", register)
        self.addSemantics("(.+)", login)
        self.addExceptionHandling(UnknownPlayer, "Nie von dir gehoert ! Wie heisst du ?")

class PasswordContext (Context):
    
    def __init__ (self):
        Context.__init__(self)
        self.addSemantics("(.+)", password)
        self.addExceptionHandling(BadPassword, "Das Passwort ist falsch")

class NameChoiceContext (Context):
    
    def __init__(self):
        Context.__init__(self)
        self.addSemantics("([a-zA-Z0-9]+)", chooseName)
        self.addExceptionHandling(PlayerExists, "Diesen Spieler gibt es bereits")
        self.addExceptionHandling(UnknownAction, "Spielernamen duerfen nur Zahlen und Buchstaben enthalten")

class PasswordChoiceContext (Context):
    
    def __init__(self):
        Context.__init__(self)
        self.addSemantics("(.+)", choosePassword)
        

class BasicContext (Context):
    
    def __init__ (self):
        Context.__init__(self)
        
        self.addSemantics("(osten)",walk)
        self.addSemantics("(westen)",walk)
        self.addSemantics("(norden)",walk)
        self.addSemantics("(sueden)",walk)
        
        self.addSemantics("(nordosten)",walk)
        self.addSemantics("(nordwesten)",walk)
        self.addSemantics("(suedosten)",walk)
        self.addSemantics("(suedwesten)",walk)
        
        self.addSemantics("(hoch)",walk)
        self.addSemantics("(runter)",walk)
        
        ######################################################
        
        self.addSemantics("nimm (.+)",take)
        self.addSemantics("wirf (.+) weg",throwAway)
        self.addSemantics("benutze (.+)",use)
        self.addSemantics("lege (.+) weg",unuse)
        self.addSemantics("stecke (.+) in (.+)",putInto)
        self.addSemantics("nimm (.+) aus (.+)",takeOut)
    
        ######################################################
        
        self.addSemantics("inv",showInventory)
        self.addSemantics("info",showInfo)
        
        self.addSemantics("schau",showRoom)
    
        self.addSemantics("untersuche (.+)",examine)
        self.addSemantics("unt (.+)",examine)
        
        self.addSemantics("gib ([a-zA-Z]+) ([a-zA-Z]+)",giveTo)
        
        #self.addSemantics("sag (.+)",say)
        #self.addSemantics("rufe (.+)",shout)
        #self.addSemantics("teile (.+) mit (.+)",sayTo)
        
        self.addSemantics("schlafe ein",logout)
        
        self.addSemantics("toete (.+)",kill)
        
        
        #################################################################
        
        self.addExceptionHandling(UnknownAction, "Wie bitte?")
        self.addExceptionHandling(ImpossibleAction, "Das ist unmoeglich")
        self.addExceptionHandling(ImprovementNotAllowed, "Du hast nicht genuegend Attributpunkte")
        self.addExceptionHandling(CharacterNotFound, "Hier ist niemand der so heisst")
        self.addExceptionHandling(NoSuchDirection, "Es gibt keinen solchen Ausgang")
        self.addExceptionHandling(AmbigousDirection, "Du bist dir nicht sicher, wohin du gehen sollst")
        self.addExceptionHandling(DetailNotFound, "So etwas siehst du nicht")
        self.addExceptionHandling(ItemNotFound, "Hier ist kein derartiger Gegenstand")
        self.addExceptionHandling(ItemNotInUse, "Du benutzt keinen derartigen Gegenstand")
        self.addExceptionHandling(UnusableItem, "Das kannst du nicht benutzen")
        self.addExceptionHandling(NotABin, "Das ist kein Behaelter")
        self.addExceptionHandling(UnsuitableBin, "Das kannst du da nicht hineinstecken")
        self.addExceptionHandling(ItemReceiverNotFound, "Hier ist niemand der so heisst")
        self.addExceptionHandling(UnsuitableItem, "Das kannst du da nicht hineinstecken")
        self.addExceptionHandling(UnsupportedUseAlias, "Das kannst du so nicht benutzen")
        self.addExceptionHandling(UnsupportedUnuseAlias, "Das kannst du so nicht weglegen")
        self.addExceptionHandling(CantAttackThisCharacter,"Du kannst gegen diesen Spieler nicht kaempfen")
