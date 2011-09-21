#!/usr/bin/python

from twisted.internet import reactor

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


class MUDServer ():
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    """
    

    def __init__ (self):
        self.factory = None


    def run (self,port):
    
        """ 
            Starts the game controller and the underlying server
            
            @param port: an integer to specify the port, the server should run on
            @raise AttributeError: if controller wasn't initialized

        """ 

        print '\033[1;42mStatus\033[1;m Starting GameController'
        
        
        factory = self.factory
        
        # start the reactor
        reactor.listenTCP(port, factory)
        print '\033[1;42mStatus\033[1;m Now Listening on port ' + str(port)
        reactor.run()