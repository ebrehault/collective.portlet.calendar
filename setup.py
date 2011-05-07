# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join("collective", "portlet", "calendar", "version.txt")).read().strip()

setup(name='collective.portlet.calendar',
      version=version,
      description="Extended Calendar Portlet: A configurable implementation of a Calendar Portlet for Plone.",
      long_description=open(os.path.join("collective", "portlet", "calendar", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone plone4 portlet calendar web',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='https://bitbucket.org/simplesconsultoria/collective.portlet.calendar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

