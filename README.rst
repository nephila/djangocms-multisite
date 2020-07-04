===================
djangocms-multisite
===================

`django-multisite <https://github.com/ecometrica/django-multisite>`_ support for DjangoCMS

|Gitter| |PyPiVersion| |PyVersion| |Status| |TestCoverage| |CodeClimate| |License|

Support
=======

Supported *Django* versions:

* Django 3.0
* Django 2.2

Supported django CMS versions:

* django CMS 3.7

Assumptions
===========

#. A virtualenv up and runnign
#. DjangoCMS working

Installation
============

``pip install djangocms-multisite``

Usage
=====

#. Open your ``settings.py`` file

#. We need to add the configurations for `django-multisite <https://github.com/ecometrica/django-multisite>`_ :

   * Replace SITE_ID value with the SiteID function::

        from multisite import SiteID
        SITE_ID = SiteID(default=1)

   * Add ``multisite``, ``djangocms_multisite`` to ``INSTALLED_APPS``::

        INSTALLED_APPS=[
            ...
            'multisite',
            'djangocms_multisite',
            ...
        ]
   * Add those loders in the TEMPLATES setting::

        TEMPLATES = [
            ...
            {
                ...
                'DIRS': {...}
                'OPTIONS': {
                    'loaders': (
                        'multisite.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    )
                }
                ...
            }
            ...
        ]

   * For other settings (cache, etc.) check the `django-multisite <https://github.com/ecometrica/django-multisite>`_ page

#. Add ``multisite.middleware.DynamicSiteMiddleware`` and ``djangocms_multisite.middleware.CMSMultiSiteMiddleware`` to ``MIDDLEWARE_CLASSES``. The order is important: ``multisite.middleware.DynamicSiteMiddleware`` must be applied before ``cms.middleware.utils.ApphookReloadMiddleware``, while ``djangocms_multisite.middleware.CMSMultiSiteMiddleware`` must be right after::

    MIDDLEWARE_CLASSES = [
        ...
        'multisite.middleware.DynamicSiteMiddleware',
        'cms.middleware.utils.ApphookReloadMiddleware',
        'djangocms_multisite.middleware.CMSMultiSiteMiddleware',
        ...
    ]

#. Configure the URL mapping as follows. The `tests.test_utils.urls1` path can be the main urlconf file that you already have in your project. And it can be the same for all the domains if you need the same structure.::

    MULTISITE_CMS_URLS={
        'www.example.com': 'tests.test_utils.urls1',
        'www.example2.com': 'tests.test_utils.urls2',
    }
    MULTISITE_CMS_ALIASES={
        'www.example.com': ('alias1.example.com', 'alias2.example.com',),
        'www.example2.com': ('alias1.example2.com', 'alias2.example2.com',),
    }
    MULTISITE_CMS_FALLBACK='www.example.com'

#. Run ``python manage.py makemigrations``

#. Run ``python manage.py migrate`` to apply the `django-multisite <https://github.com/ecometrica/django-multisite>`_ migrations


Settings explanation
====================

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

Troubleshooting
===============

* Domains in ``MULTISITE_CMS_URLS`` must be the same created in your database (via the interface in ``Home › Sites › Sites``).



.. |Gitter| image:: https://img.shields.io/badge/GITTER-join%20chat-brightgreen.svg?style=flat-square
    :target: https://gitter.im/nephila/applications
    :alt: Join the Gitter chat

.. |PyPiVersion| image:: https://img.shields.io/pypi/v/djangocms-multisite.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-multisite
    :alt: Latest PyPI version

.. |PyVersion| image:: https://img.shields.io/pypi/pyversions/djangocms-multisite.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-multisite
    :alt: Python versions

.. |Status| image:: https://img.shields.io/travis/nephila/djangocms-multisite.svg?style=flat-square
    :target: https://travis-ci.org/nephila/djangocms-multisite
    :alt: Latest Travis CI build status

.. |TestCoverage| image:: https://img.shields.io/coveralls/nephila/djangocms-multisite/master.svg?style=flat-square
    :target: https://coveralls.io/r/nephila/djangocms-multisite?branch=master
    :alt: Test coverage

.. |License| image:: https://img.shields.io/github/license/nephila/djangocms-multisite.svg?style=flat-square
   :target: https://pypi.python.org/pypi/djangocms-multisite/
    :alt: License

.. |CodeClimate| image:: https://codeclimate.com/github/nephila/djangocms-multisite/badges/gpa.svg?style=flat-square
   :target: https://codeclimate.com/github/nephila/djangocms-multisite
   :alt: Code Climate
