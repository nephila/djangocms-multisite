#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from tempfile import mkdtemp

from multisite import SiteID


def gettext(s): return s


HELPER_SETTINGS = dict(
    ROOT_URLCONF='tests.test_utils.urls1',
    INSTALLED_APPS=[
        'multisite',
        'djangocms_text_ckeditor',
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
        'www.example2.com': ('alias1.example2.com', 'alias2.example2.com', 'alias3.example2.com:8000'),
    },
    MULTISITE_CMS_FALLBACK='www.example.com',
    ALLOWED_HOSTS=['*'],
)

try:
    import djangocms_blog  # NOQA
    HELPER_SETTINGS['INSTALLED_APPS'].extend([
        'filer',
        'easy_thumbnails',
        'aldryn_apphooks_config',
        'cmsplugin_filer_image',
        'parler',
        'taggit',
        'taggit_autosuggest',
        'meta',
        'djangocms_blog',
    ])
    HELPER_SETTINGS['THUMBNAIL_PROCESSORS'] = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    )
    HELPER_SETTINGS['META_SITE_PROTOCOL'] = 'http'
    HELPER_SETTINGS['META_USE_SITES'] = True
except ImportError:
    pass


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_multisite')


def setup():
    import sys
    from djangocms_helper import runner
    runner.setup('djangocms_multisite', sys.modules[__name__], use_cms=True)


if __name__ == '__main__':
    run()
