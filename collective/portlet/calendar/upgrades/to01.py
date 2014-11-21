# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

# BBB: this seem's doin nothing


def upgrade0to1(context):
    ''' Upgrade to version 1.0
    '''
    setup = getToolByName(context, 'portal_setup')
    catalog = getToolByName(context,'portal_catalog')
    portal_properties = getToolByName(context,'portal_properties')
    
    # Do Stuff
    