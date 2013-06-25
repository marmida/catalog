'''
Manage CouchDB
'''
import subprocess
import time

class CouchManager(object):
    def __init__(self, couchdb_bin):
        self.couchdb_bin = couchdb_bin

    def __enter__(self):
        subprocess.check_call([self.couchdb_bin, '-b'])
        return self

    def __exit__(self, exc_type, exc_val, tb):
        subprocess.check_call([self.couchdb_bin, '-d'])

def run(couchdb_bin):
    with CouchManager(couchdb_bin):
        while True:
            time.sleep(0.1)