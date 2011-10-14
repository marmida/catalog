from paste import httpserver
from webob.dec import wsgify
from webob import exc
from webob import Response
from routes import Mapper, URLGenerator


class Application(object):
    map = Mapper()
    map.connect('index', '/', method='index')

    @wsgify
    def __call__(self, req):
        results = self.map.routematch(environ=req.environ)
        if not results:
            return exc.HTTPNotFound()
        match, route = results
        link = URLGenerator(self.map, req.environ)
        req.urlvars = ((), match)
        kwargs = match.copy()
        method = kwargs.pop('method')
        req.link = link
        return getattr(self, method)(req, **kwargs)

    def index(self, req):
        return Response('Hello')


def main():
    app = Application()
    httpserver.serve(app, host='127.0.0.1', port=8080)

if __name__ == '__main__':
    main()
