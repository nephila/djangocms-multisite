from urllib.parse import urlparse

from cms.utils.apphook_reload import reload_urlconf
from django.conf import settings
from django.urls import set_urlconf
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


class CMSMultiSiteMiddleware(MiddlewareMixin):
    @staticmethod
    def _get_sites():
        return getattr(settings, "MULTISITE_CMS_URLS", {})

    @staticmethod
    def _get_aliases():
        return getattr(settings, "MULTISITE_CMS_ALIASES", {})

    @classmethod
    def _get_domain(cls, request):
        """
        Check current request domain against configured domains and alias
        """
        sites = cls._get_sites()
        aliases = cls._get_aliases()
        parsed = urlparse(request.build_absolute_uri())
        host = parsed.hostname.split(":")[0]
        if host in sites:
            return host
        else:
            for domain, hosts in aliases.items():
                if host in hosts and domain in aliases:
                    return domain

    @classmethod
    def _get_urlconf(cls, domain):
        """
        Return the urlconf for the given domain in configuration.

        If given does not match, fallback is checked.

        If domain is ``None`` or no matching urlconf if found, ``None`` is returned,
        resulting in setting the default urlconf.
        """
        sites = cls._get_sites()
        MULTISITE_CMS_FALLBACK = getattr(settings, "MULTISITE_CMS_FALLBACK", "")  # noqa
        try:
            urlconf = sites[domain]
        except KeyError:
            urlconf = None
        if not urlconf and MULTISITE_CMS_FALLBACK and MULTISITE_CMS_FALLBACK in sites.keys():
            urlconf = sites[MULTISITE_CMS_FALLBACK]
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
        patch_vary_headers(response, ("Host",))
        # set back to default urlconf
        set_urlconf(None)
        return response
