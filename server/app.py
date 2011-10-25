import json
from paste import httpserver, fileapp
from webob.dec import wsgify
from webob import exc
from webob import Response, Request
from routes import Mapper, URLGenerator
import os.path

HOST = '127.0.0.1'
PORT = 8080


class CatalogApp(object):
    map = Mapper()
    map.connect('index', '/', method='index')
    map.connect('static', '/s/{filename}', method='static')
    map.connect('tags', '/tags', method='list_tags')
    
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
        
    def list_tags(self, req):
        '''
        generate a JSON list of tags
        
        '''
        resp = Response(
            body=json.dumps([
                'Absinthe dreams',
                'Abstract Westerns',
                'Aliens',
                'Alter egos',
                'Altered states',
                'Alternative',
                'Badminton',
                'Barf',
                'Bourgeoisie',
                'Budget',
                'Bullshit',
                'Captialism',
                'Communism',
                'Construction',
                'Electrical currents',
                'Fables',
                'Furious Cats',
                'Gold rush',
                'Hammers &amp; Hamsters',
                'Librarian Propaganda',
                'Marmoset documentaries',
                'Mango production worldwide',
                'Netherlands',
                'Populism',
                'Pretentious bullshit',
                'Strychnine',
                'Tow trucks',
                'Underwater public transportation',
                'Wilted vegetables',
                'Xylophones',
                'Zoological explosions',
            ])
        )
        return resp

def main():
    app = CatalogApp()
    httpserver.serve(app, host='127.0.0.1', port=8080)

if __name__ == '__main__':
    main()
