from urllib.parse import urlparse

from cms.utils.apphook_reload import reload_urlconf
from django.conf import settings
from django.urls import set_urlconf
from django.utils.cache import patch_vary_headers


class CMSMultiSiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

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

    def __call__(self, request):
        domain = self._get_domain(request)
        urlconf = self._get_urlconf(domain)
        # Reload URL patterns before setting the thread-local urlconf so that
        # any set_urlconf call inside reload_urlconf cannot override ours.
        reload_urlconf()
        # Sets the thread-local urlconf so code outside the request/response
        # cycle (e.g. Model.get_absolute_url()) resolves URLs against the
        # correct site configuration. urlconf may be None, restoring the default.
        set_urlconf(urlconf)
        try:
            response = self.get_response(request)
        finally:
            # Guaranteed cleanup: resets the thread-local even if a BaseException
            # (e.g. SystemExit, KeyboardInterrupt) bypasses Django's exception handler.
            set_urlconf(None)
        patch_vary_headers(response, ("Host",))
        return response
