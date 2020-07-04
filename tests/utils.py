from django.test.client import RequestFactory as DjangoRequestFactory


# borrowed from django-multisite, we can't import it directly due to pytest upstream dependencies

class RequestFactory(DjangoRequestFactory):
    def __init__(self, host):
        super(RequestFactory, self).__init__()
        self.host = host

    def get(self, path, data=None, host=None, **extra):
        if host is None:
            host = self.host
        return super(RequestFactory, self).get(path=path, data=data, HTTP_HOST=host, **extra)
