from urllib.parse import urlparse

from cms.utils.apphook_reload import reload_urlconf
from django.conf import settings
from django.urls import set_urlconf
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


class CMSMultiSiteMiddleware(MiddlewareMixin):
    @staticmethod
    def _get_domain(request):
        """
        Check current request domain against configured domains and alias
        """
        MULTISITE_CMS_URLS = getattr(settings, 'MULTISITE_CMS_URLS', {})
        MULTISITE_CMS_ALIASES = getattr(settings, 'MULTISITE_CMS_ALIASES', {})
        parsed = urlparse(request.build_absolute_uri())
        host = parsed.hostname.split(':')[0]
        if host in MULTISITE_CMS_URLS:
            return host
        else:
            for domain, hosts in MULTISITE_CMS_ALIASES.items():
                if host in hosts and domain in MULTISITE_CMS_URLS:
                    return domain

    @staticmethod
    def _get_urlconf(domain):
        """
        Return the urlconf for the given domain in configuration.

        If given does not match, fallbacks are checked.

        If domain is ``None`` or no matching urlconf if found, ``None`` is returned,
        resulting in setting the default urlconf.
        """
        MULTISITE_CMS_URLS = getattr(settings, 'MULTISITE_CMS_URLS', {})
        MULTISITE_CMS_FALLBACK = getattr(settings, 'MULTISITE_CMS_FALLBACK', '')
        try:
            urlconf = MULTISITE_CMS_URLS[domain]
        except KeyError:
            urlconf = None
        if (
            not urlconf and
            MULTISITE_CMS_FALLBACK and
            MULTISITE_CMS_FALLBACK in MULTISITE_CMS_URLS.keys()
        ):
            urlconf = MULTISITE_CMS_URLS[MULTISITE_CMS_FALLBACK]
        return urlconf

    def process_request(self, request):
        domain = self._get_domain(request)
        urlconf = self._get_urlconf(domain)
        # sets urlconf for current thread, so that code that does not know
        # about the request (e.g MyModel.get_absolute_url()) get the correct
        # urlconf.
        # urlconf might be None, in that case, the default is set
        set_urlconf(urlconf)
        reload_urlconf()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Host',))
        # set back to default urlconf
        set_urlconf(None)
        return response
