'''
Database routines and thread isolation
'''

import os
import sqlite3
import tempfile


import mocks


class Op(object):
    '''
    A deferred callback that captures results in member vars.
    '''

    def __init__(self, *args, **kwargs):
        '''
        Define what to call when this instance is invoked like a callable
        '''
        self.fn = args[0]
        self.args = args[1:]
        self.kwargs = kwargs
    

    def __call__(self):
        '''
        Run the target callable with the args provided.
        '''
        self.payload = self.fn(*self.args, **self.kwargs)
        
class DbManager(object):
    def __init__(self, queue):
        self.queue = queue
        self._continue = True

    def _get_db_path(self):
        '''
        return the path to the database
        '''
        return os.path.join(tempfile.mkdtemp(), 'catalog.db')

    def __call__(self):
        '''
        create a connection to the database and then go into an infinite loop,
        handling requests from a Queue
        '''
        # create the database
        self.db = sqlite3.connect(self._get_db_path())
        
        # populate the db with mock data
        mocks.populate_db(self.db)
        
        # processing loop
        while self._continue:
            # fetch the first item from the queue and execute it
            self.queue.get()()
            # let the queue know we've handled this task
            self.queue.task_done()

    def list_tags(self):
        '''
        return a list of available tags
        '''
        with self.db:
            return self.db.execute('select name from tags order by name asc').fetchall()

    def shutdown(self):
        'mark this thread for exit'
        # let's quit on the next while loop iteration
        self._continue = False
