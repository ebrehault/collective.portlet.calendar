*************************
Extended Calendar Portlet
*************************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

This package provides a configurable implementation of a Calendar Portlet.

It is possible to give the calendar portlet a header, to search only for events 
with given **keywords**, a set of **review states** and constrain its results
to only an area of your site, selecting a root folder.

If filters given by portlet's configuration panel are not enough, you can
select a **collection** instead of a folder, and all given criteria will be
used to filter yours events.

Even though Plone's default Calendar Portlet implementation is useful for most
sites if you want to segment calendar's events or to provide more than one
calendar per page, Extended Calendar Portlet comes to rescue.

Mostly Harmless
---------------

.. image:: https://secure.travis-ci.org/collective/collective.portlet.calendar.png?branch=master
    :alt: Travis CI badge
    :target: http://travis-ci.org/collective/collective.portlet.calendar

.. image:: https://coveralls.io/repos/collective/collective.portlet.calendar/badge.png?branch=master
    :alt: Coveralls badge
    :target: https://coveralls.io/r/collective/collective.portlet.calendar

Got an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`opening a support ticket`: https://github.com/collective/collective.portlet.calendar/issues

Don't Panic
-----------

Installation
^^^^^^^^^^^^

To enable this package in a buildout-based installation:

#. Edit your buildout.cfg and add add the following to it::

    [buildout]
    ...
    eggs =
         collective.portlet.calendar

After updating the configuration you need to run ''bin/buildout'', which will
take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``collective.portlet.calendar`` and click the 'Activate'
button.

.. Note::
    You may have to empty your browser cache and save your resource registries
    in order to see the effects of the product installation.

Screenshot
----------

.. image:: https://github.com/collective/collective.portlet.calendar/raw/master/screenshot.png
    :align: center
    :scale: 50%
