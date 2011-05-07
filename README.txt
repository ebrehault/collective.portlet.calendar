.. contents:: Table of Contents
   :depth: 2

Extended Calendar Portlet
****************************************

Overview
--------

This package provides a configurable implementation of a Calendar Portlet. 

It is possible to give the calendar portlet a header, to search only for events 
with given keywords and constrain its results to only an area of your site.

Even though Plone's default Calendar Portlet implementation is useful for most 
sites if you want to segment calendar's events or to provide more than one 
calendar per page, Extended Calendar Portlet comes to rescue.

Screenshot
-----------

    .. image:: http://www.simplesconsultoria.com.br/tecnologia/plone/produtos/collective.portlet.calendar/collective.portlet.calendar-0.5-screenshot.png/image_preview?

Requirements
------------

    - Plone >= 4.0.x (http://plone.org/products/plone)

Installation
------------
    
To enable this product,on a buildout based installation:

    1) Edit your buildout.cfg and add ``collective.portlet.calendar``
       to the list of eggs to install ::
    
        [buildout]
        ...
        eggs = 
             collective.portlet.calendar
    

After updating the configuration you need to run the ''bin/buildout'',
which will take care of updating your system.

Go to the 'Site Setup' page in the Plone interface and click on the
'Add/Remove Products' link.

Choose the product (check its checkbox) and click the 'Install' button.

Uninstall -- This can be done from the same management screen, but only
if you installed it from the quick installer.

Note: You may have to empty your browser cache and save your resource registries
in order to see the effects of the product installation.

Contributing
--------------

    Code repository and isssue tracker can be found at 
    `BitBucket <https://bitbucket.org/simplesconsultoria/collective.portlet.calendar>`_

Sponsoring
----------

Development of this product was sponsored by `TRT13 <http://www.trt13.jus.br>`_.


Credits
-------
    
    * Simples Consultoria (products at simplesconsultoria dot com dot br) - 
      Implementation
    
