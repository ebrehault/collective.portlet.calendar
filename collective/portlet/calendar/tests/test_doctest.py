# -*- coding: utf-8 -*-

import unittest2 as unittest
import doctest

from plone.testing import layered

from collective.portlet.calendar.testing import FUNCTIONAL_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('tests/functional.txt',
                                     package='collective.portlet.calendar'),
                layer=FUNCTIONAL_TESTING),
    ])
    return suite
