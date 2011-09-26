#!/usr/bin/python

class ContextError (StandardError):
    def __init__(self, arg):
        self.args = arg 
        
class PlayerError (ContextError):
    pass

class Invisible (PlayerError):
    pass

class NoOdor (PlayerError):
    pass

class NoFeeling (PlayerError):
    pass

class NoSound (PlayerError):
    pass


