from unittest import mock

from app_helper.base_test import BaseTestCase
from django.contrib.sites.models import Site
from django.http import Http404, HttpResponse
from django.test import override_settings
from django.urls import get_urlconf
from multisite.middleware import DynamicSiteMiddleware
from multisite.models import Alias

from djangocms_multisite.middleware import CMSMultiSiteMiddleware

from .utils import RequestFactory


class CMSMultiSiteMiddlewareTest(BaseTestCase):
    def setUp(self):
        Site.objects.all().delete()
        self.site = Site.objects.create(pk=1, domain="www.example.com")
        self.site2 = Site.objects.create(pk=2, domain="www.example2.com")

    def test_match_domain(self):
        """Resolve the request domain against the list of configured main and aliases."""
        request = RequestFactory(host="www.example.com").get("/")
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), "www.example.com")

        request = RequestFactory(host="alias1.example.com").get("/")
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), "www.example.com")

        request = RequestFactory(host="alias3.example.com").get("/")
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), None)

        request = RequestFactory(host="blabla.com").get("/")
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), None)

        request = RequestFactory(host="www.example2.com").get("/")
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), "www.example2.com")

        request = RequestFactory(host="alias2.example2.com").get("/")
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), "www.example2.com")

        # port is always ignored, only domain is considered
        request = RequestFactory(host="alias2.example2.com:8000").get("/")
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), "www.example2.com")

        # don't set port in MULTISITE_CMS_ALIASES, otherwise it will not be matched
        request = RequestFactory(host="alias3.example2.com:8000").get("/")
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), None)

    def test_match_urlconf(self):
        """Match main domain return the correct one - Any other domain -including alias- return the default."""
        self.assertEqual(CMSMultiSiteMiddleware._get_urlconf("www.example.com"), "tests.test_utils.urls1")
        self.assertEqual(CMSMultiSiteMiddleware._get_urlconf("www.example2.com"), "tests.test_utils.urls2")
        self.assertEqual(CMSMultiSiteMiddleware._get_urlconf("alias1.example.com"), "tests.test_utils.urls1")
        self.assertEqual(CMSMultiSiteMiddleware._get_urlconf("alias2.example2.com"), "tests.test_utils.urls1")

    def _get_urlconf_during_request(self, host):
        """Run the middleware and return the urlconf observed inside get_response."""
        captured = []

        def get_response(request):
            captured.append(get_urlconf())
            return HttpResponse("")

        CMSMultiSiteMiddleware(get_response)(RequestFactory(host=host).get("/"))
        return captured[0]

    @override_settings(SITE_ID=1)
    def test_process_site_1(self):
        self.assertEqual(self._get_urlconf_during_request("www.example.com"), "tests.test_utils.urls1")
        self.assertEqual(self._get_urlconf_during_request("alias1.example.com"), "tests.test_utils.urls1")

    @override_settings(SITE_ID=2)
    def test_process_site_2(self):
        self.assertEqual(self._get_urlconf_during_request("www.example2.com"), "tests.test_utils.urls2")
        self.assertEqual(self._get_urlconf_during_request("alias2.example2.com"), "tests.test_utils.urls2")

        # don't set port in MULTISITE_CMS_ALIASES, otherwise it will not be matched
        self.assertEqual(self._get_urlconf_during_request("alias3.example2.com"), "tests.test_utils.urls1")
        self.assertEqual(self._get_urlconf_during_request("alias3.example2.com:8000"), "tests.test_utils.urls1")

    @override_settings(SITE_ID=2)
    def test_urlconf_restored_after_request(self):
        """urlconf is reset to None after each completed request."""
        for host in ("www.example2.com", "alias2.example2.com"):
            CMSMultiSiteMiddleware(lambda r: HttpResponse(""))(RequestFactory(host=host).get("/"))
            self.assertIsNone(get_urlconf(), msg=f"urlconf not cleaned up for host {host}")

    def test_urlconf_restored_after_exception(self):
        """urlconf is reset to None even when a BaseException escapes the inner handler."""
        captured_inside = []

        def raise_system_exit(request):
            captured_inside.append(get_urlconf())
            raise SystemExit("simulated crash")

        with self.assertRaises(SystemExit):
            CMSMultiSiteMiddleware(raise_system_exit)(RequestFactory(host="www.example.com").get("/"))

        # The urlconf was set during the request
        self.assertEqual(captured_inside[0], "tests.test_utils.urls1")
        # And was cleaned up despite the BaseException
        self.assertIsNone(get_urlconf())


class CMSMultiSiteMiddlewareAliasTest(BaseTestCase):
    def setUp(self):
        Site.objects.all().delete()
        self.site = Site.objects.create(pk=1, domain="www.example.com")
        self.site2 = Site.objects.create(pk=2, domain="www.example2.com")
        # django-multisite2 creates canonical Alias rows automatically via
        # post_save_site_created when Site objects are saved above, so we only
        # need to create the non-canonical aliases here.
        # redirect_to_canonical defaults to True in django-multisite2; set it
        # False for aliases that should pass through to CMSMultiSiteMiddleware.
        Alias.objects.create(domain="alias1.example.com", site=self.site, redirect_to_canonical=False)
        Alias.objects.create(domain="alias2.example.com", site=self.site, redirect_to_canonical=True)
        Alias.objects.create(domain="alias1.example2.com", site=self.site2, redirect_to_canonical=False)
        Alias.objects.create(domain="alias2.example2.com", site=self.site2, redirect_to_canonical=True)

    def _get_urlconf_during_request(self, host):
        """
        Simulate DynamicSiteMiddleware + CMSMultiSiteMiddleware in sequence
        and return the urlconf observed inside get_response.
        Only valid for hosts where DynamicSiteMiddleware calls through
        (canonical aliases and redirect_to_canonical=False aliases).
        """
        captured = []

        def capture_get_response(req):
            captured.append(get_urlconf())
            return HttpResponse("")

        request = RequestFactory(host=host).get("/")
        DynamicSiteMiddleware(CMSMultiSiteMiddleware(capture_get_response))(request)
        return captured[0]

    def test_process_site_1(self):
        # Canonical domain: DynamicSiteMiddleware calls through
        self.assertEqual(self._get_urlconf_during_request("www.example.com"), "tests.test_utils.urls1")
        # Non-redirect alias: DynamicSiteMiddleware calls through
        self.assertEqual(self._get_urlconf_during_request("alias1.example.com"), "tests.test_utils.urls1")

    def test_process_site_2(self):
        # Canonical domain: DynamicSiteMiddleware calls through
        self.assertEqual(self._get_urlconf_during_request("www.example2.com"), "tests.test_utils.urls2")
        # Non-redirect alias: DynamicSiteMiddleware calls through
        self.assertEqual(self._get_urlconf_during_request("alias1.example2.com"), "tests.test_utils.urls2")

        # Hosts unknown to DynamicSiteMiddleware raise Http404
        request = RequestFactory(host="alias3.example2.com").get("/")
        with self.assertRaises(Http404):
            DynamicSiteMiddleware(mock.MagicMock(return_value=HttpResponse("")))(request)
