import json
import os.path
from paste import httpserver, fileapp
from routes import Mapper, URLGenerator
from webob.dec import wsgify
from webob import exc
from webob import Response, Request



import mocks

HOST = '127.0.0.1'
PORT = 8080


class CatalogApp(object):
    map = Mapper()
    map.connect('index', '/', method='index')
    map.connect('static', '/s/{filename}', method='static')
    map.connect('tags', '/tags', method='list_tags')
    map.connect('matches', '/matches/{tag_name}', method='match_search')
    
    CLIENT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'client'))

    def __init__(self):
        self.dirapp = fileapp.DirectoryApp(self.CLIENT_PATH)

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
        # set the PATH_INFO to just filename, overriding the original URI 
        req.environ['PATH_INFO'] = 'index.html'
        return req.get_response(self.dirapp)
        
    def static(self, req, filename=None):
        # set the PATH_INFO to just filename, overriding the original URI 
        req.environ['PATH_INFO'] = filename
        return req.get_response(self.dirapp)
        
    def _mock_handler(self, fn):
        '''
        build a response, given a mock function
        '''
        resp = Response(
            body=json.dumps(fn())
        )
        return resp
        
    def list_tags(self, req):
        '''
        generate a JSON list of tags
        
        '''
        return self._mock_handler(mocks.list_tags)
        
    def match_search(self, req, tag_name=None):
        '''
        generate a JSON list of dicts, one per match
        '''
        return self._mock_handler(mocks.match_search)

def main():
    app = CatalogApp()
    httpserver.serve(app, host='127.0.0.1', port=8080)

if __name__ == '__main__':
    main()
