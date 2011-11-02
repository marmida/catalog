'''
Database routines and thread isolation
'''

import os
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
            # fetch the first item from the queue and execute it
            self.queue.get()()
            # let the queue know we've handled this task
            self.queue.task_done()

    def list_tags(self):
        with self.db.transaction:
            tag_root_node = self.db.reference_node.TAGS.single.endNode
            result = [tag_rel.endNode['name'] for tag_rel in tag_root_node.IS_TAG]
    
        return result

