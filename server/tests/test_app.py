import unittest
from webob import Request

import app

class DirAppTest(unittest.TestCase):
    def test_fetch_index(self):
        'Application.dirapp: fetches index.html from \'client\' directory'
        
        # get an Application instance
        application = app.CatalogApp()
        
        # build a request to its index page and send to dirapp
        req = Request.blank('index.html')
        resp = req.get_response(application.dirapp)
        
        print 'response status %s body %s' % (resp.status, resp.body)
        
        # assertions on returned page
        self.assertTrue('Catalog' in resp.body)
        self.assertEquals('200 OK', resp.status)
        
    def test_unknown_uri(self):
        # get an Application instance
        application = app.CatalogApp()
        
        # build a request to its index page and send to dirapp
        req = Request.blank('unknown-file')
        resp = req.get_response(application.dirapp)
        
        print 'response status %s body %s' % (resp.status, resp.body)
        
        # assertions on returned page
        self.assertTrue('404' in resp.status)
