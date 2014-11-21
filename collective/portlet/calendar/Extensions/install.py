# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger('collective.portlet.calendar')

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.runAllImportStepsFromProfile('profile-collective.portlet.calendar:uninstall')
        logger.info("Uninstall done")
