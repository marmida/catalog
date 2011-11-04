'''
Database routines and thread isolation
'''

import os
import sqlite3
import tempfile


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
    '''
    Segregated interaction with the database; meant to be used as a callable
    target for a threading.Thread instance.  Fetches callables a Queue and 
    processes them.  Exits once the _contiue attr is False.  
    '''
    def __init__(self, queue, path):
        self.queue = queue
        self._continue = True
        self.path = path

    def __call__(self):
        '''
        create a connection to the database and then go into an infinite loop,
        handling requests from a Queue
        '''
        # create the database connection
        self.db = sqlite3.connect(self.path)
        
        if not self._schema_exists():
            self._create_schema()
        
        # processing loop
        while self._continue:
            # fetch the first item from the queue and execute it
            self.queue.get()()
            # let the queue know we've handled this task
            self.queue.task_done()
            
    # schema creation
    def _schema_exists(self):
        '''
        return True if the schema has already been created in this db
        '''
        return 'tags' in [i[0] for i in self.db.execute('select name from sqlite_master')]
    
    def _create_schema(self):
        '''
        create the necessary tables in the database
        '''
        with self.db:
            # create "tags" table
            self.db.execute('''create table tags 
                (
                    id INTEGER PRIMARY KEY,
                    name varchar(50) not null
                )'''
            )
    
    # normal db routines
    def list_tags(self):
        '''
        return a list of available tags
        '''
        with self.db:
            return [i[0] for i in self.db.execute('select name from tags order by name asc')]
            
    def match_search(self):
        '''
        return a list of dicts, one per match, associated with a tag
        '''
        with self.db:
            return []
            
    def file_info(self, req, file_path=None):
        '''
        generate a JSON object describing a single file
        '''
        return {}

    def shutdown(self):
        '''
        Mark this thread for exit.
        
        Originally this needed to be a thread-isolated callback, just like the 
        other db functions, because neo4j.GraphDatabase.shutdown had to be 
        called.  Now that we're back to sqlite, it's probably unnecessary.
        '''
        # let's quit on the next while loop iteration
        self._continue = False
