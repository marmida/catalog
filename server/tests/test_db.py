'''
tests for the db.py module
'''

import sqlite3
import tempfile
import unittest

import db

class ArgCapture(object):
    def __init__(self, retval=None):
        self.retval = retval
        self.call_count = 0
    
    def __call__(self, *args, **kwargs):
        self.call_count += 1
        
        self.args = args
        self.kwargs = kwargs

        return self.retval

class OpTest(unittest.TestCase):
    def test_no_args(self):
        '''
        db.Op: works without any args
        '''
        capture = ArgCapture()
        db.Op(capture)()
        self.assertEquals(capture.call_count, 1)
        
    def test_retval(self):
        '''
        db.Op: captures return values
        '''
        capture = ArgCapture('hello')
        op = db.Op(capture)
        op()
        self.assertEquals('hello', op.payload)
        
    def test_args(self):
        '''
        db.Op: passes args and kwargs
        '''
        capture = ArgCapture()
        op = db.Op(capture, 123, '456', seven_eight_nine=789)
        op()
        self.assertEquals((123, '456'), capture.args)
        self.assertEquals({'seven_eight_nine': 789}, capture.kwargs)
        
class DbManagerInitTest(unittest.TestCase):
    '''
    test DbManager handling setup of a new database
    '''
    def test_schema_exists(self):
        with tempfile.NamedTemporaryFile() as fp:
            dbm = db.DbManager(None, fp.name)
            # mock setup
            dbm._continue = False
            dbm._create_schema = lambda :None
            dbm() # should exit after one run, create 'db' attr
            self.assertFalse(dbm._schema_exists())
            
        with tempfile.NamedTemporaryFile() as fp:
            dbm = db.DbManager(None, fp.name)
            # mock setup
            dbm._continue = False
            dbm._create_schema = lambda :None
            dbm() # should exit after one run, create 'db' attr
            # create a table named 'tags' and the schema should "exist"
            with dbm.db:
                dbm.db.execute('create table tags (id INTEGER PRIMARY KEY, hullaballoo varchar(1))')
            self.assertTrue(dbm._schema_exists())
            
    def test_create_schema(self):
        with tempfile.NamedTemporaryFile() as fp:
            dbm = db.DbManager(None, fp.name)
            # mock setup
            dbm._continue = False
            dbm() # should exit after one run, create 'db' attr, populate db
            
            with dbm.db:
                self.assertTrue('tags' in [i[0] for i in dbm.db.execute('select name from sqlite_master')])
        
class DbManagerExtantTest(unittest.TestCase):
    '''
    test DbManager with an existing database
    '''
    def setUp(self):
        self.dbfile = tempfile.NamedTemporaryFile()
        self.db = sqlite3.connect(self.dbfile.name)
        
        with self.db:
            self.db.execute('create table tags (id INTEGER PRIMARY KEY, name varchar(30))')
        with self.db:
            for i in ['hello', 'goodbye', 'what']:
                self.db.execute('insert into tags (name) values (?)', (i,))
            
        
    def tearDown(self):
        self.dbfile.close() 
    
    def test_list_tags(self):
        '''
        DbManager.list_tags: generates a list
        '''
        dbm = db.DbManager(None, self.dbfile.name)
        # mock setup - let the db manager run and exit
        dbm._continue = False
        dbm()
        
        self.assertEquals(['goodbye', 'hello', 'what'], dbm.list_tags())
        
class DbManagerTest(unittest.TestCase):
    '''
    test DbManager methods
    '''
    def setUp(self):
        self.temp_fp = tempfile.NamedTemporaryFile()
        self.dbm = db.DbManager(None, self.temp_fp.name)
        self.dbm.db = sqlite3.connect(self.temp_fp.name)
        self.dbm._create_schema()
        
    def tearDown(self):
        self.temp_fp.close()
        
    def test_create_or_update(self):
        '''
        DbManager.create_or_update_tag: creates a tag, and then update it in a second call. 
        '''
        self.dbm.create_or_update_tag('Hello')
        self.assertEquals(['Hello'],  [i[0] for i in self.dbm.db.execute('select name from tags')])
        
        self.dbm.create_or_update_tag('Goodbye', 'Hello')
        self.assertEquals(['Goodbye'],  [i[0] for i in self.dbm.db.execute('select name from tags')])
        
        self.assertRaises(ValueError, self.dbm.create_or_update_tag, 'apples', 'oranges')

