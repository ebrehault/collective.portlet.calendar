Changelog
---------

1.0b3 (unreleased)
^^^^^^^^^^^^^^^^^^

- Drop support for Plone 4.0 and 4.1.
  [hvelarde]

- Remove also browserlayer when running unistall profile. [keul]
- Uninstall profiles was not run on uninstall [keul]
- Removed useless paster generated code (there's no Archetypes contents there).
  [keul]
- Support for new-style collections from plone.app.collection package.
  This **drop Plone 3.3 compatibility**. [keul]
- Removed kss attributes and added modern HTML 5 ones. This make the
  calendar JavaScript works on Plone 4.3. [keul]
- Links to search page are @@ prefixed. [keul]
- Fixed issue when not providing a portlet name. [keul]
- Fixed layout: when not providing a title, the portlet looks like default
  Plone calendar. [keul]
- Fixed portlet cache key. It was not looking for additional paramenters.
  [keul]
- Calendar portlet title in management screen were stored forever. [keul]

1.0b2 (2012-05-10)
^^^^^^^^^^^^^^^^^^

- Added basic installation tests. [hvelarde]


1.0b1 (2012-05-10)
^^^^^^^^^^^^^^^^^^

- Tested Plone 4.2 compatibility. [hvelarde]

- Updated package information and development buildout configurations.
  [hvelarde]

- Added Basque translation. [shagi]


0.6 (2011-05-19)
^^^^^^^^^^^^^^^^

- Added Italian translation. [keul]

- Added Brazilian Portuguese translation. [erico_andrei]

- Now also Plone 3.3 compatible. [keul]

- Change the translation domain, fixing all the i18ndude stuff (that were not
  working), because while using the "plone" ones was not possible to translate
  anything. [keul]

- Selecting a collection, all other filters are ignored (if you want a
  review_state or Subject filter, put it in the collection itself). [keul]

- Added and fixed tests. [keul]

- Minimal pyflakes changes. [keul]


0.5 (2011-05-06)
^^^^^^^^^^^^^^^^

- Providing a base css to our portlet. [erico_andrei]

- Allows restricting the results to only a subset of the site. [erico_andrei]

- Adding portlet name/title. [erico_andrei]

- Initial release. [erico_andrei]

