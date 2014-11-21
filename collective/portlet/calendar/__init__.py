# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory as BaseMessageFactory

from collective.portlet.calendar import config

from Products.Archetypes import atapi
from Products.CMFCore import utils

MessageFactory = BaseMessageFactory('collective.portlet.calendar')

def initialize(context):
    pass