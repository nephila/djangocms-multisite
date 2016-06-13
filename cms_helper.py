#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os

from tempfile import mkdtemp


def gettext(s): return s
from multisite import SiteID

HELPER_SETTINGS = dict(
    ROOT_URLCONF='tests.test_utils.urls1',
    INSTALLED_APPS=[
        'multisite',
        'djangocms_text_ckeditor'
    ],
    LANGUAGE_CODE='en',
    LANGUAGES=(
        ('en', gettext('English')),
    ),
    CMS_LANGUAGES={
        1: [
            {
                'code': 'en',
                'name': gettext('English'),
                'public': True,
            },
        ],
        2: [
            {
                'code': 'en',
                'name': gettext('English'),
                'public': True,
            },
        ],
        'default': {
            'hide_untranslated': False,
        },
    },
    MIDDLEWARE_CLASSES=(
        'multisite.middleware.DynamicSiteMiddleware',
        'djangocms_multisite.middleware.CMSMultiSiteMiddleware',
    ),
    MIGRATION_MODULES={},
    USE_TZ=True,
    TIME_ZONE='UTC',
    FILE_UPLOAD_TEMP_DIR=mkdtemp(),
    SITE_ID=SiteID(default=1),
    MULTISITE_CMS_URLS={
        'www.example.com': 'tests.test_utils.urls1',
        'www.example2.com': 'tests.test_utils.urls2',
    },
    MULTISITE_CMS_ALIASES={
        'www.example.com': ('alias1.example.com', 'alias2.example.com',),
        'www.example2.com': ('alias1.example2.com', 'alias2.example2.com',),
    },
    MULTISITE_CMS_FALLBACK='www.example.com'
)


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_multisite')


def setup():
    import sys
    from djangocms_helper import runner
    runner.setup('djangocms_multisite', sys.modules[__name__], use_cms=True)

if __name__ == '__main__':
    run()
