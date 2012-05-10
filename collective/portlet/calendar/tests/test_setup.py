# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.browserlayer.utils import registered_layers

from collective.portlet.calendar.config import PROJECTNAME
from collective.portlet.calendar.testing import INTEGRATION_TESTING


class InstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = getattr(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_browserlayer_installed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertTrue('ICalendarExLayer' in layers,
                        'browser layer was not installed')

    def test_css_registry(self):
        portal_css = self.portal.portal_css
        resources = portal_css.getResourceIds()
        self.assertTrue('++resource++calendar_styles/calendar.css' in resources)


class UninstallTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.qi = getattr(self.portal, 'portal_quickinstaller')
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_browserlayer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertFalse('ICalendarExLayer' in layers,
                         'browser layer was not removed')

    def test_css_registry_removed(self):
        portal_css = self.portal.portal_css
        resources = portal_css.getResourceIds()
        self.assertFalse('++resource++calendar_styles/calendar.css' in resources)
