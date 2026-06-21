from django.apps import AppConfig


class DjangoCMSMultisiteConfig(AppConfig):
    name = "djangocms_multisite"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        self._override_site_id_check()

    @staticmethod
    def _override_site_id_check():
        from django.core.checks import Error, Tags, register, registry

        # Remove Django's built-in check that requires SITE_ID to be a plain int.
        # django-multisite2 sets SITE_ID to a SiteID (threading.local subclass)
        # that is not an int subclass, so int(SITE_ID) raises TypeError at
        # system-check time before any request has set the active site.
        registry.registered_checks = {
            fn
            for fn in registry.registered_checks
            if not (
                getattr(fn, "__name__", "") == "check_site_id"
                and getattr(fn, "__module__", "") == "django.contrib.sites.checks"
            )
        }

        @register(Tags.models)
        def check_site_id(app_configs, **kwargs):
            from django.conf import settings
            from multisite import SiteID

            site_id = getattr(settings, "SITE_ID", "")
            if site_id and not isinstance(site_id, (int, SiteID)):
                try:
                    int(site_id)
                except (TypeError, ValueError):
                    return [
                        Error(
                            "The SITE_ID setting must be an integer.",
                            id="sites.E101",
                        )
                    ]
            return []
