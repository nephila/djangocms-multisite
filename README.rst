===================
djangocms-multisite
===================

.. image:: https://img.shields.io/pypi/v/djangocms-multisite.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-multisite
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/djangocms-multisite.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-multisite
    :alt: Monthly downloads

.. image:: https://img.shields.io/pypi/pyversions/djangocms-multisite.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-multisite
    :alt: Python versions

.. image:: https://img.shields.io/travis/nephila/djangocms-multisite.svg?style=flat-square
    :target: https://travis-ci.org/nephila/djangocms-multisite
    :alt: Latest Travis CI build status

.. image:: https://img.shields.io/coveralls/nephila/djangocms-multisite/master.svg?style=flat-square
    :target: https://coveralls.io/r/nephila/djangocms-multisite?branch=master
    :alt: Test coverage

.. image:: https://img.shields.io/codecov/c/github/nephila/djangocms-multisite/develop.svg?style=flat-square
    :target: https://codecov.io/github/nephila/djangocms-multisite
    :alt: Test coverage

.. image:: https://codeclimate.com/github/nephila/djangocms-multisite/badges/gpa.svg?style=flat-square
   :target: https://codeclimate.com/github/nephila/djangocms-multisite
   :alt: Code Climate

django-multisite support for django CMS

Supported Django versions:

* Django 1.6
* Django 1.7
* Django 1.8
* Django 1.9

Supported django CMS versions:

* django CMS 3.*

Usage
=====

#. Configure django-multisite as documented upstream

#. Use ``SITE_ID = SiteId(default=1)`` instead of the documented ``SITE_ID = SiteID()``


#. Add ``multisite``, ``djangocms_multisite`` to ``INSTALLED_APPS``::

    INSTALLED_APPS=[
        ...
        'multisite',
        'djangocms_multisite',
        ...
    ]

#. Add ``djangocms_multisite.middleware.CMSMultiSiteMiddleware`` to ``MIDDLEWARE_CLASSES`` after
   ``django-multisite`` middleware::

    MIDDLEWARE_CLASSES = [
        ...
        'multisite.middleware.DynamicSiteMiddleware',
        'djangocms_multisite.middleware.CMSMultiSiteMiddleware',
        ...
    ]

#. Configure the URL mapping as follows::

    MULTISITE_CMS_URLS={
        'www.example.com': 'tests.test_utils.urls1',
        'www.example2.com': 'tests.test_utils.urls2',
    },
    MULTISITE_CMS_ALIASES={
        'www.example.com': ('alias1.example.com', 'alias2.example.com',),
        'www.example2.com': ('alias1.example2.com', 'alias2.example2.com',),
    },
    MULTISITE_CMS_FALLBACK='www.example.com'
    
#. Run ``python manage.py migrate``


Settings
========

MULTISITE_CMS_URLS
^^^^^^^^^^^^^^^^^^

Dictionary (or OrderedDict) containing the mapping between the domain (as configured in django
``sites``) and the corresponding urlconf.

MULTISITE_CMS_FALLBACK
^^^^^^^^^^^^^^^^^^^^^^

The default domain to load if any of the above does not match.

MULTISITE_CMS_ALIASES
^^^^^^^^^^^^^^^^^^^^^

Dictionary (or OrderedDict) containing the mapping between the domain (as configured in django
``sites``) and a list of aliases. This is optional if all the aliases are configured as
``django-multisite`` aliases
