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

    # connection lifecycle
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
    
    def shutdown(self):
        '''
        Mark this thread for exit.
        
        Originally this needed to be a thread-isolated callback, just like the 
        other db functions, because neo4j.GraphDatabase.shutdown had to be 
        called.  Now that we're back to sqlite, it's probably unnecessary.
        '''
        # let's quit on the next while loop iteration
        self._continue = False
    
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
        table_schemas = [
            ('tags', ['id INTEGER PRIMARY KEY', 'name varchar(50) not null']),
            ('files', ['id INTEGER PRIMARY KEY', 'path varchar(255) not null']),
            ('map_tags_files', ['tag_id integer not null', 'file_id integer not null']),
        ]
        
        for i in table_schemas:
            with self.db:
                # create "tags" table
                self.db.execute('''
                    create table %s 
                    (
                        %s
                    )''' % (i[0], ', '.join(i[1]))
                )
    
    # db access and modification routines
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
        
    def create_or_update_tag(self, new_tag_name, old_tag_name=None):
        '''
        create a new tag, or update an old tag with a new name
        '''
        with self.db:
            # prevent duplicates
            if self.db.execute('select count(*) as ct from tags where name=?', (new_tag_name,)).fetchone()[0] > 0:
                raise ValueError('tag already exists: %s' % new_tag_name)
        
        with self.db:
            try: 
                old_tag_id = self.db.execute('select id from tags where name=?', (old_tag_name,)).fetchone()[0] \
                        if old_tag_name else False
            except TypeError:
                # fetchone() returned None; so our subscript caused a TypeError
                raise ValueError('original tag name does not exist: %s' % old_tag_name)
        
        with self.db:
            if old_tag_name:
                if not old_tag_id:
                    raise Exception('uh oh')
                self.db.execute('update tags set name=? where id=?', (new_tag_name, old_tag_id))
            else:
                self.db.execute('insert into tags (name) values (?)', (new_tag_name,))
                
    def delete_tag(self, tag_name):
        '''
        Delete a tag and its relationships to any files
        '''
        tag_id = self.db.execute('select id from tags where name=?', (tag_name,)).fetchone()[0]
        with self.db:
            self.db.execute('delete from map_tags_files where tag_id = ?', (tag_id,))
            self.db.execute('delete from tags where id = ?', (tag_id,))
            
