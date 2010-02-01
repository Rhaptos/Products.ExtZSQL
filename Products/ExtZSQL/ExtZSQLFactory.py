"""
External ZSQL Factory

Provides an 'SQL'/ZSQL Method factory to return 'SQL' objects given filesystem
files. This is primarily for use by Python-based products, but could have
applications for TTW development as well. The factory

 * Exists only once for each connection given to it.

 * Returns a reference to a ZSQL Method (an 'SQL' object) given a filename.

 * Makes sure only one 'SQL' object exists for each file.

 * Allows refreshing any or all of its contained ZSQL Methods

Author: J Cameron Cooper (extzsql@jcameroncooper.com)
(C) 2003-2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
# apologies to strict Pythoners for my use of studlyCaps; that's what we do here

import os
import stat
from os import path
import ExtZSQLMethod

__version__='0.1'

# a dictionary with key:connection_id and value:factoryInstance
__factory_dict = {}

def getFactory(connection_id):
    """Method to return the proper ExtZSQLFactory for a given DB connection.

    There is only one factory per connection, and this function either returns
    an existing one or creates a new one.
    """
    cnxn_id = str(connection_id)
    if __factory_dict.has_key(cnxn_id):
        return __factory_dict[cnxn_id]
    else:
        new_factory = ExtZSQLFactory(cnxn_id)
        __factory_dict[cnxn_id] = new_factory
        return new_factory
    assert false  # we should never get here
    return None

class Statement:
    """Simple data containment class for the 'statement' concept."""
    def __init__(self, sql, change_info):
        self.sql = sql
        self.change_info = change_info
    
class ExtZSQLFactory:
    """Factory for producing 'SQL' objects from files.

    connection_id - identifier of some database connection, extant or future.
    """

    def __init__(self, connection_id):
        self.connection_id = str(connection_id)
        self.__statement_dict = {}

    def connectionIsValid(self):
        """Checks if connection is extant and connected. Unused currently.

        Stolen from Shared.DC.ZRDB.DA
        """
        return (hasattr(self, self.connection_id) and
                hasattr(getattr(self, self.connection_id), 'connected'))

    def getStatement(self,filename,context):
        """Returns a statement based on the contents of the filename.

        If we have done this before, we return the already made one if
        no changes have been made. If changes have been made, a refresh is
        triggered before the statement is returned.
        """
        filename_abs_path = path.abspath(filename)   # phooey on relative paths
        
        if self.__statement_dict.has_key(filename_abs_path):
            # we have this already
            if self.__changedStatement(filename_abs_path):
                # ... but it changed, so refresh it
                self.__statement_dict[filename_abs_path].sql.refresh()
                # self.__setStatement(filename_abs_path) # this makes a new one
        else:
            # we don't have this, so make it
            self.__setStatement(filename_abs_path)
        return self.__statement_dict[filename_abs_path].sql.__of__(context)

    def refresh_all(self):
        """Trigger a forcible refresh on all current methods."""
        for extsql in __statement_dict.values():
            extsql.refresh()


    def __setStatement(self,filename):
        """Creates a new statement from the given file and stores it.

        filename is expected to be an absolute path to avoid replication
        due to relative paths.

        Should be considered private.
        """
        if path.isfile(filename):
            #f = open(filename)
            #sql = f.readlines()
            sql = ExtZSQLMethod.ExtZSQLMethod(self.__mkid(filename),
                                              filename,
                                              self.connection_id,
                                              filename)
            statement = Statement(sql,self.__changeInfo(filename))
            self.__statement_dict[filename] = statement
        else:
            print "Not a valid file!"

    def __changeInfo(self,filename):
        """Hook for generating change info.

        Given a filename, returns whatever data is needed for
        '__changedStatement' to determine if cahnge has occurred. Is called by
        '__setStatement' upon creation. Overriding the two change... methods
        is all that is necessary to change out the refresh decision.
        """
        return os.stat(filename)[stat.ST_MTIME]

    def __changedStatement(self,filename):
        """Heuristically determines if the file has changed since last checked.

        Currently based on timestamp, but could be based on CVS versions or
        straight up diffs with stored full text.
        """
        new = self.__changeInfo(filename)
        old = self.__statement_dict[filename].change_info
        return new != old

    def __mkid(self,filename):
        """Create a hopefully unique id for our (mostly anonymous) ExtZSQLMethods.
        """
        # got this from a runyaga post on ZopeLabs. so blame him.
        import whrandom
        from DateTime import DateTime

        return str(DateTime().strftime('%Y%m%d%H%M%S')
                   ) + "." + str(whrandom.random())[2:]
