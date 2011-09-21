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


class ContextError (StandardError):
    def __init__(self, arg):
        self.args = arg 
        
class PlayerError (ContextError):
    pass

class UnknownAction (PlayerError):
    pass

class ImpossibleAction (PlayerError):
    pass

class DebugMessage (StandardError):
    pass



class PlayerNotFound (PlayerError):
    pass

class CharacterNotFound (PlayerError):
    pass

class ItemReceiverNotFound (PlayerError):
    pass



class CantAttackThisCharacter (PlayerError):
    pass

class NoSubscription (PlayerError):
    pass

class UnknownChannel (PlayerError):
    pass


class GroupNotFound (PlayerError):
    pass

class ItemNotFound (PlayerError):
    pass

class ItemNotInUse (PlayerError):
    pass

class ItemTooBig (PlayerError):
    pass

class ItemTooHeavy (PlayerError):
    pass

class UnwearableItem (PlayerError):
    pass

class UnusableItem (PlayerError):
    pass

class UnsuitableBin (PlayerError):
    pass


class NotAKey (PlayerError):
    pass

class NotABin (PlayerError):
    pass

class ItemNotInBin (PlayerError):
    pass

class UnsuitableItem (PlayerError):
    pass

class CannotIncreaseAttribute (PlayerError):
    pass

class LoginException (StandardError):
    pass

class UnknownPlayer (LoginException):
    pass

class BadPassword (LoginException):
    pass

class NoSuchDirection (PlayerError):
    pass

class UnsuitableCharacter (PlayerError):
    pass

class UnsuitableDetail (PlayerError):
    pass

class RegisterException (ContextError):
    pass

class UnknownPlayerType (RegisterException):
    pass

class PlayerExists (RegisterException):
    pass

class DetailNotFound (PlayerError):
    pass

class DoorLocked (PlayerError):
    pass

class WrongKey (PlayerError):
    pass

class NotADoor (PlayerError):
    pass

class NotAPortal (PlayerError):
    pass

class ImprovementNotAllowed (PlayerError):
    pass

class AmbigousDirection (PlayerError):
    pass