from ormapping import Persistent, String, Reference
from hashlib import sha512

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

class User (Persistent):
    
    """ 
    @author: Fabian Vallon 
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1
    
    Saves a (Username,Password) pair
    """
    
    login = String()
    sha512password = String()
    lastlocation = Reference()
    
    def __init__ (self):
        Persistent.__init__(self)
        self.login = ""
        self.lastlocation = None
    
    def getPassword (self):
        return self.sha512password
    
    def setPassword (self,pw):
        self.sha512password = sha512(pw).hexdigest()
    
    password = property(getPassword,setPassword)