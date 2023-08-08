from cms.utils.conf import get_cms_setting
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve

admin.autodiscover()

urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT, "show_indexes": True}),
    re_path(
        r"^media/cms/(?P<path>.*)$", serve, {"document_root": get_cms_setting("MEDIA_ROOT"), "show_indexes": True}
    ),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += i18n_patterns(
    re_path(r"^admin/", admin.site.urls),
    path("", include("cms.urls")),
)
