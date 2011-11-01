'''
Database routines and thread isolation
'''

import os
import tempfile


import mocks
import models


class DbThread(object):
    def __init__(self, queue):
        self.queue = queue

    def _get_db_path(self):
        '''
        return the path to the database
        '''
        return os.path.join(tempfile.mkdtemp())

    def __call__(self):
        '''
        create a connection to the database and then go into an infinite loop,
        handling requests from a Queue
        '''
        # don't import until we're in the new thread
        import neo4j
        
        # create the database
        self.db = neo4j.GraphDatabase(self._get_db_path())
        
        # populate the db with mock data
        mocks.populate_db(self.db)
        
        # processing loop
        while True:
            request = self.queue.get()
            request.response = models.list_tags(self.db)
            self.queue.task_done()
