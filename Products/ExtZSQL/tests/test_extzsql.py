#------------------------------------------------------------------------------#
#   test_extzsql.py                                                            #
#                                                                              #
#       Authors:                                                               #
#       Rajiv Bakulesh Shah <raj@enfoldsystems.com>                            #
#                                                                              #
#           Copyright (c) 2009, Enfold Systems, Inc.                           #
#           All rights reserved.                                               #
#                                                                              #
#               This software is licensed under the Terms and Conditions       #
#               contained within the "LICENSE.txt" file that accompanied       #
#               this software.  Any inquiries concerning the scope or          #
#               enforceability of the license should be addressed to:          #
#                                                                              #
#                   Enfold Systems, Inc.                                       #
#                   4617 Montrose Blvd., Suite C215                            #
#                   Houston, Texas 77006 USA                                   #
#                   p. +1 713.942.2377 | f. +1 832.201.8856                    #
#                   www.enfoldsystems.com                                      #
#                   info@enfoldsystems.com                                     #
#------------------------------------------------------------------------------#
"""Unit tests.
$Id: $
"""


from Products.RhaptosTest import config
config.products_to_install = ['ExtZSQL']

from Products.ExtZSQL.ExtZSQLFactory import getFactory
from Products.RhaptosTest import base


class TestExtZSQL(base.RhaptosTestCase):

    def afterSetUp(self):
        self.factory = getFactory('connection')
        self.sql_file_path = './src/Products.ExtZSQL/Products/ExtZSQL/tests/test2.sql'

    def beforeTearDown(self):
        pass

    def test_extzsql_factory(self):
        results = self.factory.getStatement(self.sql_file_path, self.portal)
        # TODO: Flesh out this test to make sure that we're actually getting
        # results.


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExtZSQL))
    return suite
