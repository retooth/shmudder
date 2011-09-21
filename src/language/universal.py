#!/usr/bin/python

import re
from basic.exceptions import UnknownAction

class Semantics (object):
    
    def __init__ (self,regex,actionf):
        self.regex   = regex
        self.actionf = actionf
    
    def match (self,command):
        
        m = re.findall(self.regex,command)
        
        if not m:
            return False
        
        first = m[0]
        
        if type(first) == tuple:
            return first
        
        if type(first) == str:
            return (m[0],)




class Context (object):
    
    """ parses string commands and handles
    context specific exceptions. """
    
    def __init__ (self):

        
        self.semantics = []
        
        # a dict<type,str>, that contains exception types as
        # keys and strings as values
        self.exceptionlang = {}
    
    def addSemantics (self, regex, actionf):
        s = Semantics(regex, actionf)
        self.semantics.append(s)

    def addExceptionHandling (self,exceptiontype,answer):
        self.exceptionlang[exceptiontype] = answer
    
    def parse (self,command):
        
        """ parses a string according to context semantics """
        
        for s in self.semantics:
            arguments = s.match(command)
            if arguments :
                return (s.actionf,s.regex,arguments)
                break
        
        raise UnknownAction("")
        
    
    def handle (self,player,error):
        
        """ handles context specific errors """
        # get type
        errtype = type(error)
        if self.exceptionlang.has_key(errtype):
            player.receiveMessage(self.exceptionlang[errtype])
        
        
    def showWelcome (self, handler):
        raise NotImplementedError(str(type(self))+": Lack of showWelcome() method")
    
    def showGoodBye (self, handler):
        raise NotImplementedError(str(type(self))+": Lack of showGoodbye() method")
