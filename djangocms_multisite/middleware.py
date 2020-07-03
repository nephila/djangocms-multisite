# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.utils.apphook_reload import reload_urlconf
from django.conf import settings
from django.urls import set_urlconf
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin
from urllib.parse import urlparse


class CMSMultiSiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        MULTISITE_CMS_URLS = getattr(settings, 'MULTISITE_CMS_URLS', {})
        MULTISITE_CMS_ALIASES = getattr(settings, 'MULTISITE_CMS_ALIASES', {})
        MULTISITE_CMS_FALLBACK = getattr(settings, 'MULTISITE_CMS_FALLBACK', '')
        try:
            parsed = urlparse(request.build_absolute_uri())
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
            try:
                # In django CMS 3.4.2 this allows us to save a few queries thanks to per-site appresolvers caching
                reload_urlconf(clear_cache=False)
            except TypeError:
                reload_urlconf()
        except KeyError:
            # use default urlconf (settings.ROOT_URLCONF)
            set_urlconf(None)

    def process_response(self, request, response):
        patch_vary_headers(response, ('Host',))
        # set back to default urlconf
        set_urlconf(None)
        return response
