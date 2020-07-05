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
        self.site = Site.objects.create(pk=1, domain='www.example.com')
        self.site2 = Site.objects.create(pk=2, domain='www.example2.com')

    def test_match_domain(self):
        """Resolve the request domain against the list of configured main and aliases."""
        request = RequestFactory(host='www.example.com').get('/')
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), 'www.example.com')

        request = RequestFactory(host='alias1.example.com').get('/')
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), 'www.example.com')

        request = RequestFactory(host='alias3.example.com').get('/')
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), None)

        request = RequestFactory(host='blabla.com').get('/')
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), None)

        request = RequestFactory(host='www.example2.com').get('/')
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), 'www.example2.com')

        request = RequestFactory(host='alias2.example2.com').get('/')
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), 'www.example2.com')

        # port is always ignored, only domain is considered
        request = RequestFactory(host='alias2.example2.com:8000').get('/')
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), 'www.example2.com')

        # don't set port in MULTISITE_CMS_ALIASES, otherwise it will not be matched
        request = RequestFactory(host='alias3.example2.com:8000').get('/')
        self.assertEqual(CMSMultiSiteMiddleware._get_domain(request), None)

    def test_match_urlconf(self):
        """Match main domain return the correct one - Any other domain -including alias- return the default."""
        self.assertEqual(CMSMultiSiteMiddleware._get_urlconf('www.example.com'), 'tests.test_utils.urls1')
        self.assertEqual(CMSMultiSiteMiddleware._get_urlconf('www.example2.com'), 'tests.test_utils.urls2')
        self.assertEqual(CMSMultiSiteMiddleware._get_urlconf('alias1.example.com'), 'tests.test_utils.urls1')
        self.assertEqual(CMSMultiSiteMiddleware._get_urlconf('alias2.example2.com'), 'tests.test_utils.urls1')

    @override_settings(SITE_ID=1)
    def test_process_site_1(self):
        request = RequestFactory(host='www.example.com').get('/')
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls1')

        request = RequestFactory(host='alias1.example.com').get('/')
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls1')

    @override_settings(SITE_ID=2)
    def test_process_site_2(self):
        request = RequestFactory(host='www.example2.com').get('/')
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls2')

        request = RequestFactory(host='alias2.example2.com').get('/')
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls2')

        # don't set port in MULTISITE_CMS_ALIASES, otherwise it will not be matched
        request = RequestFactory(host='alias3.example2.com').get('/')
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls1')

        # don't set port in MULTISITE_CMS_ALIASES, otherwise it will not be matched
        request = RequestFactory(host='alias3.example2.com:8000').get('/')
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls1')

    @override_settings(SITE_ID=2)
    def test_process_reponse(self):
        request = RequestFactory(host='www.example2.com').get('/')
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls2')
        CMSMultiSiteMiddleware().process_response(request, HttpResponse(''))
        # Default is restored after request is processed
        self.assertIsNone(get_urlconf())

        request = RequestFactory(host='alias2.example2.com').get('/')
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls2')
        CMSMultiSiteMiddleware().process_response(request, HttpResponse(''))
        # Default is restored after request is processed
        self.assertIsNone(get_urlconf())


class CMSMultiSiteMiddlewareAliasTest(BaseTestCase):
    def setUp(self):
        Site.objects.all().delete()
        self.site = Site.objects.create(pk=1, domain='www.example.com')
        self.site2 = Site.objects.create(pk=2, domain='www.example2.com')
        Alias.objects.create(domain='alias1.example.com', site=self.site)
        Alias.objects.create(domain='alias2.example.com', site=self.site, redirect_to_canonical=True)

        Alias.objects.create(domain='alias1.example2.com', site=self.site2)
        Alias.objects.create(domain='alias2.example2.com', site=self.site2, redirect_to_canonical=True)

    def test_process_site_1(self):
        request = RequestFactory(host='www.example.com').get('/')
        DynamicSiteMiddleware().process_request(request)
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls1')

        request = RequestFactory(host='alias1.example.com').get('/')
        DynamicSiteMiddleware().process_request(request)
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls1')

    def test_process_site_2(self):
        request = RequestFactory(host='www.example2.com').get('/')
        DynamicSiteMiddleware().process_request(request)
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls2')

        request = RequestFactory(host='alias2.example2.com').get('/')
        DynamicSiteMiddleware().process_request(request)
        CMSMultiSiteMiddleware().process_request(request)
        self.assertEqual(get_urlconf(), 'tests.test_utils.urls2')

        # aliases not configured on django-multisite will not be recognizes
        request = RequestFactory(host='alias3.example2.com').get('/')
        with self.assertRaises(Http404):
            DynamicSiteMiddleware().process_request(request)
