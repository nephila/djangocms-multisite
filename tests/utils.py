from django.test.client import RequestFactory as DjangoRequestFactory


class RequestFactory(DjangoRequestFactory):
    # borrowed from django-multisite, we can't import it directly due to pytest upstream dependencies
    def __init__(self, host):
        super().__init__()
        self.host = host

    def get(self, path, data=None, host=None, **extra):
        if host is None:
            host = self.host
        return super().get(path=path, data=data, HTTP_HOST=host, **extra)
