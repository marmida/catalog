import configobj
import json
import os.path
import paste.fileapp
import paste.httpserver
import Queue
import routes
import threading
import webob
import webob.dec
import webob.exc


import db


HOST = '127.0.0.1'
PORT = 8080

CONFIG_DIR = '~/.marmida_catalog'
CONFIG_FILENAME = 'config'
DATABASE_FILENAME = 'db'


class CatalogApp(object):
    map = routes.Mapper()
    map.connect('index', '/', method='index')
    map.connect('static', '/s/{filename}', method='static')
    map.connect('tags', '/tags', method='list_tags')
    map.connect('matches', '/matches/{tag_name}', method='match_search')
    map.connect('file_info', '/file/{file_path:.*?}', method='file_info')
    
    CLIENT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www'))

    def __init__(self):
        # create a dirapp for serving static content
        self.dirapp = paste.fileapp.DirectoryApp(self.CLIENT_PATH)
        
        # get the current configuration
        self.config = self._get_config()
        
        # create the database
        self.db_queue = Queue.Queue()
        self.db_manager = db.DbManager(self.db_queue, self.config['db_path'])
        self.db_thread = threading.Thread(group=None, target=self.db_manager)
        self.db_thread.daemon = True # exit the app when the main thread quits
        self.db_thread.start()
        
    # configuration handling
    def _get_config(self):
        '''
        Return a ConfigObj instance representing the current configuration values
        If no configuration is currently on disk, create one with defaults
        '''
        config_path = os.path.expanduser(os.path.join(CONFIG_DIR, CONFIG_FILENAME))
        if not os.path.exists(config_path):
            return self._create_default_config(config_path)
        return configobj.ConfigObj(config_path)
        
    def _create_default_config(self, path):
        '''
        Create a config file with sensible defaults and return a ConfigObj
        '''
        config_dir = os.path.dirname(path)
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)
        
        config = configobj.ConfigObj()
        config.filename = path
        config['db_path'] = os.path.join(config_dir, DATABASE_FILENAME)
        config.write()
        return config
        
    # context manager support: handle database shutdown on exit
    def __enter__(self):
        'no-op; database init is handled in the constructor (is this wise?)'
        return self
        
    def __exit__(self, exc_type, exc_val, tb):
        'try to shutdown the database'
        print 'shutting down...'
        
        # empty out the queue
        while not self.db_queue.empty():
            self.db_queue.get(False)
            self.db_queue.task_done()
        
        # enqueue a shutdown request and block until it finishes
        self.db_queue.put(db.Op(self.db_manager.shutdown))
        # join to the thread, not the queue, which should block until it exits
        self.db_thread.join()
        
        # no need to suppress exceptions
        
        print '...done'

    @webob.dec.wsgify
    def __call__(self, req):
        results = self.map.routematch(environ=req.environ)
        if not results:
            return webob.exc.HTTPNotFound()
        match, route = results
        link = routes.URLGenerator(self.map, req.environ)
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
    
    def _db_op(self, fn, *args, **kwargs):
        '''
        Run a callable in the database thread and return the result.
        '''
        op = db.Op(fn, *args, **kwargs)
        self.db_queue.put(op)
        self.db_queue.join()

        return op.payload

    # entry points from routes
    # todo: figure out how to unify these; they're very repetitive
    def list_tags(self, req):
        '''
        generate a JSON list of tags
        
        '''
        return _json_response(self._db_op(self.db_manager.list_tags))
        
    def match_search(self, req, tag_name=None):
        '''
        generate a JSON list of dicts, one per match, associated with a tag
        '''
        return _json_response(self._db_op(self.db_manager.match_search, tag_name))
        
    def file_info(self, req, file_path=None):
        '''
        generate a JSON object describing a single file
        '''
        return _json_response(self._db_op(self.db_manager.file_info, file_path))

# todo: turn into a decorator
def _json_response(obj):
    '''
    build a response, given a function
    '''
    resp = webob.Response(
        body=json.dumps(obj)
    )
    return resp

def main():
    with CatalogApp() as app:
        paste.httpserver.serve(app, host=HOST, port=PORT)

if __name__ == '__main__':
    main()
