Changelog
---------

1.0b4 (unreleased)
^^^^^^^^^^^^^^^^^^

- Fixed and issue with default review_states set, that was of tuple type,
  so catalog uncompatible
  [keul]


1.0b3 (2015-07-07)
^^^^^^^^^^^^^^^^^^

- Change in the review state usage behavior: if no value is specified do not
  use the global site settings (that was a bit unexpected) but do not filter
  by review state at all.
  [keul]
- Be sure that start/end criteria in collections never use values outside the
  current month
  [keul]
- Fixed issue that make calendar display weird days when Collections use start
  or end criteria as calendar machinery already do
  [keul]
- Calendar URI querystring parameters are now applied when root object is used
  [keul]
- Fixed issue in the ``_render_cachekey`` method that gives some unexpected
  results with collections under certain circumstances
  [keul]
- Fixed illogical behavior with collections: if you do not provide any
  ``review_state`` filter, a static ("published", "private") was used
  [keul]
- Folder were not selectable as root object [keul]
- **Drop support for Plone 4.0 and 4.1**.
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
- Fixed portlet cache key. It was not looking for additional parameters.
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

