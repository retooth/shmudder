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


class Groupable (object):
    
    """ 
    @author: Fabian Vallon
    @license: U{GPL v3<http://www.gnu.org/licenses/>}
    @version: 0.1
    @since: 0.1

    Specifies a showGroup method, that shows objects
    of the same type as a group. This is convenient for
    objects, that exist in great quantities (like coins)
    """
    
    @classmethod
    def showGroup (cls,actor,amount):
        clsn = cls.__name__
        raise NotImplementedError(clsn+" You have to define a showGroup class method")
