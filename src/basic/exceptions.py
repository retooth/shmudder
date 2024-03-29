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


from abstract.exceptions import PlayerError

class UnknownAction (PlayerError):
    pass

class ImpossibleAction (PlayerError):
    pass

# network layer
#################################################

class UnknownPlayer (PlayerError):
    pass

class BadPassword (PlayerError):
    pass

class UnknownPlayerType (PlayerError):
    pass

class PlayerExists (PlayerError):
    pass


# player properties
#################################################

class ImprovementNotAllowed (PlayerError):
    pass

# social
#################################################

class CharacterNotFound (PlayerError):
    pass

class NoSubscription (PlayerError):
    pass

class UnknownChannel (PlayerError):
    pass

class GroupNotFound (PlayerError):
    pass


# enviroment
#################################################

class NoSuchDirection (PlayerError):
    pass

class AmbigousDirection (PlayerError):
    pass

class DetailNotFound (PlayerError):
    pass

# items
#################################################

class ItemNotFound (PlayerError):
    pass

class ItemNotInUse (PlayerError):
    pass

class UnusableItem (PlayerError):
    pass

class UneatableItem (PlayerError):
    pass

class UnwearableItem (PlayerError):
    pass

class UndrinkableItem (PlayerError):
    pass

class UnsuitableBin (PlayerError):
    pass

class NotABin (PlayerError):
    pass

class UnsuitableItem (PlayerError):
    pass

class ItemReceiverNotFound (PlayerError):
    pass

class UnsupportedUseAlias (PlayerError):
    pass

class UnsupportedUnuseAlias (PlayerError):
    pass


# fights
#################################################


class CantAttackThisCharacter (PlayerError):
    pass


# choosey collections
#################################################


class UnsuitableCharacter (PlayerError):
    pass

class UnsuitableDetail (PlayerError):
    pass