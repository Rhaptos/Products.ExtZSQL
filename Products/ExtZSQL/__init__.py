# ExtZSQLProduct
# author: J Cameron Cooper
# 12 Feb 2003
#
# Copyright 2003 J Cameron Cooper
# licensed under the GPL: see LICENSE file for details

"""Local File System product initialization"""
__version__='0.1'

import ExtZSQLMethod
import ExtZSQLFactory

def initialize(context):
    context.registerClass(ExtZSQLMethod.ExtZSQLMethod,
                          permission="Add ExtZSQL Methods",
                          constructors=(ExtZSQLMethod.manage_addExtZSQLMethodForm,
                                        ExtZSQLMethod.manage_addExtZSQLMethod),
                          icon='www/extzsql.gif'
                          )
        
