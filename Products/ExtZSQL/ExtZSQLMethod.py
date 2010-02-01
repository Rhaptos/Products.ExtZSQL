"""
External ZSQL Method Product

Coupled with the ExtZSQLFactory class, this allows ZSQL methods from the
filesystem, with a number of other benefits besides. The primary purpose
of this class is to make the SQL method uneditable, with a heavy secondary
purpose being to provide ZMI TTW capabilities (Adding persistent FS-based
ZSQL methods is a side-effect; see the Factory for details).

Of course, this somewhat replicates the CMF FSZSQLMethod, but hey,
we're not all CMF. Oh, and sorry 'bout all the acronyms.

Author: J. Cameron Cooper (extzsql@jcameroncooper.com)
(C) 2003-2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
# portions inspired by FSZSQLMethod.py from CMF

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile

from Products.ZSQLMethods import SQL
from OFS import SimpleItem

__version__='0.1'

manage_addExtZSQLMethodForm = DTMLFile('www/addExtZSQL',globals())
def manage_addExtZSQLMethod(self,id,title,connection_id,file,REQUEST=None):
    """Add an ExtZSQLMethod to a folderish object.

    connection_id - the id of some database connection (not necessarily extant)

    file - the file path of the file to be used as the SQL contents
           (in the future, possibly a URI for use with urllib2)
    """
    ob = ExtZSQLMethod(id,title,connection_id,file)
    self._setObject(id, ob)
    return self.manage_main(self, REQUEST)

class ExtZSQLMethod(SQL.SQL):
    """ZSQLMethod generated from a file.

    An ExtZSQLMethod is non-editable, and usually made by an ExtZSQLFactory.
    """
    meta_type = "External ZSQL Method"

    ## lock it down (no edits on filesystem, yet) (thanks CMF guys!)
    manage_options=(
        (
            {'label':'Summary', 'action':'manage_extZSQLSummary'},
            {'label':'Refresh', 'action':'manage_extZSQLRefresh'},
            {'label':'Test', 'action':'manage_testForm',
             'help':('ZSQLMethods','Z-SQL-Method_Test.stx')},
            )
        )

    # Use declarative security
    security = ClassSecurityInfo()
    
    # security.declareObjectProtected(View) # CMF stuff?
    # security.declareProtected(ViewManagementScreens, 'manage_customise') # CMF?
    
    # Make mutators private
    security.declarePrivate('manage_main','manage_edit',
                            'manage_advanced','manage_advancedForm')

    manage=None
    manage_extZSQLSummary=DTMLFile('www/summarizeSQL', globals())
        
    def __init__(self,id,title,connection_id,file):
        # let parent take care of its properties, but keep mine with ext_XXX
        self.id=self.ext_id=str(id)
        self.title=self.ext_title=str(title)
        self.ext_file = str(file)
        self.ext_connection_id = str(connection_id)
        self.refresh()

    manage_extZSQLRefresh=DTMLFile('www/refresh', globals())

    def refresh(self, REQUEST=None):
        """Read the file from disk and set all necessary SQLish attributes.

        All object properties with regard to query will be reset from file
        upon call. Will use file's connection_id or title if such a parameter
        is given.

        Uses the same parameters format (and code!) as the CMF's FSZSQLMethod.
        Namely a dtml-comment block with each new line having a key:value pair.

        There are hard-coded defaults for cache and max_rows, but these can
        be reset in the file by 'max_rows', 'max_cache', and 'cache_time'
        parameters.
        """
        file = open(self.ext_file,'r')  # CMF says 'rb', but I don't believe it
        try:
            data = file.read()
        finally: file.close()

        # parse parameters
        parameters = {}
        start = data.find('<dtml-comment>')
        end = data.find('</dtml-comment>')
        if start==-1 or end==-1 or start>end:
            # I think we could happily ignore this error, but...
            raise ValueError, 'Could not find parameter block'
        block = data[start+14:end]

        for line in block.split('\n'):
            pair = line.split(':',1)
            if len(pair) != 2:
                continue    # bail if we fail to gey key:value, as in a blank line
            parameters[pair[0].strip().lower()]=pair[1].strip()

        # check for required and optional parameters
        try:
            title =         parameters.get('title',self.ext_title)
            connection_id = parameters.get('connection_id',self.ext_connection_id)
            arguments =     parameters.get('arguments','')
            max_rows =      parameters.get('max_rows',1000)
            max_cache =     parameters.get('max_cache',100)
            cache_time =    parameters.get('cache_time',0)
            class_name =    parameters.get('class_name','')
            class_file =    parameters.get('class_file','')
            # one may do a raw dictionary lookup for a required parameter
        except KeyError,e:
            raise ValueError, "Parameter %s is required but was not given." % e
                                      
        self.manage_edit(title, connection_id, arguments, template=data)
        self.manage_advanced(max_rows, max_cache, cache_time, class_name, class_file)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_extZSQLSummary')
            
InitializeClass(ExtZSQLMethod)
