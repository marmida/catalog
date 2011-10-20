import json
import unittest
from webob import Request

import app

class RoutingTest(unittest.TestCase):
    '''
    Tests to ensure our routing is working correctly.
    
    '''
    
    def test_fetch_index(self):
        'Application: fetches index.html from \'client\' directory'
        
        # get an Application instance
        application = app.CatalogApp()
        
        # build a request to its index page and send to dirapp
        req = Request.blank('/')
        resp = req.get_response(application)
        
        print 'response status %s body %s' % (resp.status, resp.body)
        
        # assertions on returned page
        self.assertTrue('Catalog' in resp.body)
        self.assertEquals('200 OK', resp.status)
        
    def test_unknown_uri(self):
        'Application: 404s a completely bogus URI'
        
        # get an Application instance
        application = app.CatalogApp()
        
        # build a request to its index page and send to dirapp
        req = Request.blank('unknown-file')
        resp = req.get_response(application)
        
        print 'response status %s body %s' % (resp.status, resp.body)
        
        # assertions on returned page
        self.assertTrue('404' in resp.status)
        
    def test_tags(self):
        'Application: returns a canned list of tags for /tags'
        
        application = app.CatalogApp()
        
        # build a request to /tags and get response
        req = Request.blank('/tags')
        resp = req.get_response(application)
        
        # unpack json
        print resp.body
        tag_list = json.loads(resp.body)
        
        self.assertTrue('Librarian Propaganda' in tag_list)
