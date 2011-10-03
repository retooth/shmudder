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


import sqlite3, pickle

"""
This module implements a object relational mapping suitable for multiple inheritance
and dynamic typing. The approach is similar to the joined table inheritance in sqlalchemy.
Every layer of the object hierarchy gets its own table. To support dynamic typing, objects
have a database-wide unique id stored in the persistent class.
"""

# mainly undocumented, it's a weird hack

class DBLoadError(StandardError):
    pass


class OffcutList (object):

    """ A list that allows gaps betweens values and uses append
    to automatically fill the gaps.
    """

    def __init__ (self):
        
        # the actual objects id(int) -> object
        self.objects = {0:None}
        
        # indices of gaps
        self.gaps = []
    
    
    def getMaxFree (self):
        return max(self.objects.keys())+1
    
    maxfree  = property(fget=getMaxFree,doc="Free key with greatest value")
    
        
    def getFreeSpot (self):
        if self.gaps:
            return self.gaps.pop(0)
        return self.maxfree+1
    
    freespot = property(getFreeSpot)
    
    
    def __getitem__ (self, i):
        return self.objects[i]


    def __setitem__ (self, i, value):
        oldmaxfree = self.maxfree
        self.objects[i] = value
         
        if oldmaxfree < i :
            newgaps = range(oldmaxfree,i)
            self.gaps += newgaps
    
        elif i in self.gaps :
            self.gaps.remove(i)
        
        
    def __delitem__ (self, index):        
        del self.objects[index]
        
        if index < self.maxfree:
            self.gaps.append(index)
        
        self.gaps = filter(lambda x: x < self.maxfree, self.gaps)
        
        
    def append (self, value):
        free = self.freespot
        self[free] = value
        return free


    def values (self):
        return self.objects.values()
   
        
class Store (object):
    
    __shared_state = {}
    
    def __init__ (self, file=None):
        if file :
            self.__dict__   = Store.__shared_state
            self.objects    = OffcutList()
            self.connection = sqlite3.connect(file)
            self.cursor     = self.connection.cursor()
        else :
            self.__dict__   = Store.__shared_state
    
    def add (self,o):
        """ dumps basic data about o into the database """
        # TODO: maybe refactor this to Persitent
        o.id = self.objects.append(o)
        
        # run a bottom up BFS through the object hierarchy
        
        q = [o.__class__]
        visited = []
        
        while q != []:
            
            cls = q.pop(0)
            
            # skip, if class is not meant to be persistent
            # (could be a mixin)
            if "__class_table__" not in dir(cls):
                continue
            
            # skip if class is top end of hierarchy
            if cls is object:
                continue
            
            # skip if class was already visited
            if cls in visited:
                continue
            
            # add base classes to queue
            q += list(cls.__bases__)
            
            # class uses parents table for data
            # storing -> skip
            if cls.__name__ != cls.__class_table__ :
                continue

            # append class to visited
            visited.append(cls)
            
            #############################
            # Insert the row
            #############################
            
            t = (o.id,o.__class__.__name__)
            
            self.cursor.execute("insert into " + cls.__class_table__ + \
                                " (id,_class) values (?,?)",t)
        
        
    def load (self,locals):
        """
        Loads all store objects into memory. Should be called like
        this: mystore.load(locals())
        """
        all = self.cursor.execute("select * from Persistent").fetchall()
        
        # built all objects known in database
        
        for objdata in all :
            
            _classname = str(objdata[1])
            
            try :
                _class = locals[_classname]
            except KeyError:    
                raise DBLoadError(_classname + " is not in local scope")
             
            newobj = _class.__new__(_class)
            newobj.store = self
            
            id = objdata[0]
            self.objects[id] = newobj
                        
            newobj.id = id
            
        # synchronize objects to database
        
        tabletuples = self.cursor.execute("select tbl_name from sqlite_master").fetchall()
        
        for tuple in tabletuples :
            
            table = tuple[0]
            
            all = self.cursor.execute("select * from " + table)
            
            if str(table) not in locals :
                raise DBLoadError (str(table) + " is not in local scope")
            
            if not "__attributes__" in dir(locals[str(table)]):
                raise DBLoadError (str(table) + " is in database, but has no __attributes__ table. Maybe you altered the class.")
            
            if not type(locals[str(table)].__attributes__) == dict:
                raise DBLoadError (str(table) + " has a badly written __attributes__ class variable. This shouldn't happen. Did you define __attribute__ by yourself somewhere ?")
            
            pattern = locals[str(table)].__attributes__.keys()
            
            for entry in all:
                
                id    = entry[0]
                data  = list(entry)[2:]
                
                fresh = dict(zip(pattern,data))
                
                self.objects[id].__dict__.update(fresh)
        
        # postload
        
        for o in self.objects.values():
            if "__postload__" in dir(o):
                o.__postload__()
        
        
    def update (self, table, id, var, value):
        t = (value,id)
        self.cursor.execute("update " + table + " set " + var + "= ? where id = ?;",t)
            
            
            
                      
class Reference (object):

    """ Persistent Reference Property.
    Supports Dynamic Typing
     """

    def __get__(self, instance, owner):
        
        if not self.real in instance.__dict__:
            return None
        
        return instance.store.objects[instance.__dict__[self.real]]


    def __set__(self, instance, value):
        if not value :
            instance.__dict__[self.real] = 0
        else :
            instance.__dict__[self.real] = value.id
        instance.__update__(self.real)


class PickleType (object):

    """ Saves data as pickle string. """
    
    def __get__(self, instance, owner):
        return pickle.loads(str(instance.__dict__[self.real]))

    def __set__(self, instance, value):
        pstring = pickle.dumps(value)
        instance.__dict__[self.real] = pstring
        instance.__update__(self.real)
    

class StringList (object):
    
    def __get__(self, instance, owner):
        strrepr = instance.__dict__[self.real]
        return strrepr.split("|")

    def __set__(self, instance, value):
        strrep = "|".join(value)
        instance.__dict__[self.real] = strrep
        instance.__update__(self.real)


class String (object):

    def __init__ (self):
        pass
    
    def __get__(self, instance, owner):
        return str(instance.__dict__[self.real])

    def __set__(self, instance, value):
        instance.__dict__[self.real] = value
        instance.__update__(self.real)


class Integer (object):

    def __init__ (self):
        pass
    
    def __get__(self, instance, owner):
        return instance.__dict__[self.real]

    def __set__(self, instance, value):
        instance.__dict__[self.real] = value
        instance.__update__(self.real)


class Boolean (object):

    def __init__ (self):
        pass
    
    def __get__(self, instance, owner):
        
        if not self.real in instance.__dict__:
            return False
        
        if instance.__dict__[self.real]:
            return True
        return False

    def __set__(self, instance, value):
        if value :
            instance.__dict__[self.real] = 1
        else :
            instance.__dict__[self.real] = 0
        instance.__update__(self.real)


class BackRef (object):
    
    def __init__ (self,itemclass,ref):
        self.store = Store()
        self.itemclass = itemclass
        self.ref = "_"+ref

    def __get__(self, instance, owner):
        table = self.itemclass.__class_table__
        items = self.store.cursor.execute("select id from " + table + " where " + self.ref + "=" + str(instance.id) + ";").fetchall()
        return map(lambda x: self.store.objects[x[0]], items)

    def __set__(self, instance, value):
        raise StandardError ("Read-Only")

class OneToOne (object):
    
    def __init__ (self,itemclass,ref):
        self.store = Store()
        self.itemclass = itemclass
        self.ref = "_"+ref

    def __get__(self, instance, owner):
        table = self.itemclass.__class_table__
        item = self.store.cursor.execute("select id from " + table + " where " + self.ref + "=" + str(instance.id) + ";").fetchone()
        return self.store.objects[item[0]]

    def __set__(self, instance, value):
        raise StandardError ("Read-Only")



class PersistentMeta (type):

    # credit goes to azaq23 from #python.de
    # for suggesting the meta class approach

    def __new__(self, name, bases, d):
        
        d["__attributes__"] = {}

        for k, v in d.items():
            real = "_" + k
            if isinstance(v, String):
                d["__attributes__"][real] = "text default ''"
                v.real = real
            if isinstance(v, Integer) or isinstance (v,Reference) or isinstance(v,Boolean):
                d["__attributes__"][real] = "int default 0"
                v.real = real
            if isinstance(v, PickleType):
                d["__attributes__"][real] = "blob default 0"
                v.real = real

        if d["__attributes__"]:
            d["__class_table__"] = name

        return type.__new__(self, name, bases, d)
   

class Persistent (object):
    
    __metaclass__ = PersistentMeta

    __class_table__ = "Persistent"
    
    patchid = Integer()

    def __init__ (self):
        if not "_instore" in dir(self):
            self._instore = True
            self.store = Store()
            self.store.add(self)
    
    @classmethod
    def __rebase__ (cls):
        if cls.__name__ != cls.__class_table__:
            return
        s = Store()
        cbtuples = s.cursor.execute("PRAGMA table_info(" +  cls.__class_table__ + ");").fetchall()
        
        oldbase  = []
        for t in cbtuples:
            colname = str(t[1])
            oldbase.append(colname)

        newbase = cls.__attributes__.keys() + ["id","_class"]
        mixed   = list(set(newbase + oldbase))
        
        for attr in mixed:
            
            if attr in oldbase and attr not in newbase:
                       
                tlist = ["id","_class"]
                
                for rowname, rowtype in cls.__attributes__.items():
                    tlist.append(rowname + " " + rowtype)
                    
                tstr = "(" + ",".join(tlist) + ")"
                s = Store()
                s.cursor.execute("create temporary table " + 
                                 cls.__class_table__ + "_backup " + 
                                 tstr + ";")
                
                clist = cls.__attributes__.keys() + ["id","_class"] 
                
                                 
                s.cursor.execute("insert into " +
                                 cls.__class_table__ + "_backup " +
                                 "select " + ",".join(clist) + " " +
                                 "from " + cls.__class_table__ + ";")
                
                s.cursor.execute("drop table " + cls.__class_table__ + ";")
                
                s.cursor.execute("create table " + 
                                 cls.__class_table__ + 
                                 tstr + ";")
                
                s.cursor.execute("insert into " +
                                 cls.__class_table__ + " "
                                 "select " + ",".join(clist) + " " + " "
                                 "from " + cls.__class_table__ + "_backup;")

                s.cursor.execute("drop table " + cls.__class_table__ + "_backup;")
              
            if attr in newbase and attr not in oldbase:
                s.cursor.execute("alter table " + cls.__class_table__ + 
                                 " add column " + attr + " " +
                                 cls.__attributes__[attr])
                
            
    
    @classmethod
    def createTable (cls):
        
        """ Creates a table for this particular class
        @Warning: Method doesn't create base class tables
        """ 
        
        if cls.__name__ != cls.__class_table__ :
            return
        
        tlist = ["id","_class"]
        
        for rowname, rowtype in cls.__attributes__.items():
            tlist.append(rowname + " " + rowtype)
        tstr = "(" + ",".join(tlist) + ")"
        s = Store()
        s.cursor.execute("create table if not exists " + cls.__class_table__ + " " + tstr)
    
    @classmethod
    def getAllInstances (cls):
        s = Store()
        idtuples = s.cursor.execute("select id from Persistent where _class = ?",(cls.__name__,)).fetchall()
        objects = []
        for tuple in idtuples:
            id = tuple[0]
            objects.append(s.objects[id])
        return objects
    
    def __delete__ (self):
        
        """ Removes object from the database 
        
        @Warning: This is not reference save. Objects, that have
        a reference to this object will still store the old id.
        If a new object is added with the same id, those objects
        will point to it. This can lead to serious errors
        """

        q = [self.__class__]
        visited = []
        
        while q != []:
        
            cls = q.pop(0)
            
            # skip, if class is not meant to be persistent
            # (could be a mixin)
            if "__class_table__" not in dir(cls):
                continue
            
            # skip if class is top end of hierarchy
            if cls is object:
                continue
            
            # skip if class was already visited
            if cls in visited:
                continue
            
            # add base classes to queue
            q += list(cls.__bases__)
            
            # class uses parents table for data
            # storing -> skip
            if cls.__name__ != cls.__class_table__ :
                continue

            visited.append(cls)
            
            _table = cls.__class_table__
            t = (self.id,)
            self.store.cursor.execute("delete from " + _table + " where id = ?",t)
        
        del self.store.objects[self.id]
        
    
    def __update__ (self, attrname):
        
        """
        Updates the object attribute attrname(str) in the database
        """
        
        # looking for the class location of the attribute
        
        q = [self.__class__]
        visited = []
        
        while q != []:
        
            cls = q.pop(0)
            
            # skip, if class is not meant to be persistent
            # (could be a mixin)
            if "__class_table__" not in dir(cls):
                continue
            
            # skip if class is top end of hierarchy
            if cls is object:
                continue
            
            # skip if class was already visited
            if cls in visited:
                continue
            
            # add base classes to queue
            q += list(cls.__bases__)
            
            # class uses parents table for data
            # storing -> skip
            if cls.__name__ != cls.__class_table__ :
                continue

            visited.append(cls)
            
            attr    = cls.__attributes__.keys()
            
            # class location found: cls
            if attrname in attr:
                
                # update value 
                table = cls.__class_table__
                id    = self.id
                value = self.__dict__[attrname]
                
                self.store.update(table,id,attrname,value)
                break
