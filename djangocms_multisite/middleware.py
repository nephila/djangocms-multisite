# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.core.urlresolvers import set_urlconf
from django.utils.cache import patch_vary_headers
from django.utils.six.moves import urllib_parse as urlparse


class CMSMultiSiteMiddleware(object):
    def process_request(self, request):
        try:
            full_host = '{scheme}://{host}'.format(
                scheme=request.scheme, host=request.META['HTTP_HOST']
            )
            parsed = urlparse.urlparse(full_host)
            host = parsed.hostname
            urlconf = None
            try:
                urlconf = settings.MULTISITE_CMS_URLS[host]
            except KeyError:
                for domain, hosts in settings.MULTISITE_CMS_ALIASES.items():
                    if host in hosts:
                        urlconf = settings.MULTISITE_CMS_URLS[domain]
                        break
            if not urlconf:
                urlconf = settings.MULTISITE_CMS_URLS[settings.MULTISITE_CMS_FALLBACK]
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
