# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.core.urlresolvers import set_urlconf
from django.utils.cache import patch_vary_headers
from django.utils.six.moves import urllib_parse as urlparse


class CMSMultiSiteMiddleware(object):
    def process_request(self, request):
        MULTISITE_CMS_URLS = getattr(settings, 'MULTISITE_CMS_URLS', {})
        MULTISITE_CMS_ALIASES = getattr(settings, 'MULTISITE_CMS_ALIASES', {})
        MULTISITE_CMS_FALLBACK = getattr(settings, 'MULTISITE_CMS_FALLBACK', '')
        try:
            parsed = urlparse.urlparse(request.build_absolute_uri())
            host = parsed.hostname.split(':')[0]
            urlconf = None
            try:
                urlconf = MULTISITE_CMS_URLS[host]
            except KeyError:
                for domain, hosts in MULTISITE_CMS_ALIASES.items():
                    if host in hosts and domain in MULTISITE_CMS_URLS:
                        urlconf = MULTISITE_CMS_URLS[domain]
                        break
            if (
                not urlconf and
                MULTISITE_CMS_FALLBACK and
                MULTISITE_CMS_FALLBACK in MULTISITE_CMS_URLS.keys()
            ):
                urlconf = MULTISITE_CMS_URLS[MULTISITE_CMS_FALLBACK]

            if urlconf:
                request.urlconf = urlconf
            # sets urlconf for current thread, so that code that does not know
            # about the request (e.g MyModel.get_absolute_url()) get the correct
            # urlconf.
            set_urlconf(urlconf)
        except KeyError:
            # use default urlconf (settings.ROOT_URLCONF)
            set_urlconf(None)

    def process_response(self, request, response):
        if getattr(request, 'urlconf', None):
            patch_vary_headers(response, ('Host',))
        # set back to default urlconf
        set_urlconf(None)
        return response
