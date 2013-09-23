'''
Backend web application module.  Uses flask.
'''
from argparse import ArgumentParser
from flask import Flask
import json
import os.path
import Queue
import threading

import db

HOST = '127.0.0.1'
PORT = 8080
APP = Flask('catalog')
CLIENT_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'www'))
        
@APP.route('/tags')        
def list_tags():
    '''
    generate a JSON list of tags
    
    '''
    # TEMPORARY INSANITY: we'll remove the threading bit later.
    # JPype + Neo should be usable from all Flask threads after their bugfix
    db_queue = Queue.Queue()
    db_manager = db.DbManager(db_queue) 
    db_thread = threading.Thread(group=None, target=db_manager)
    db_thread.daemon = True # exit the app when the main thread quits
    db_thread.start()

    op = db.Op(db_manager.list_tags)
    db_queue.put(op)
    db_queue.join()

    return json.dumps(op.payload)

@APP.route('/matches/<tagname>')        
def match_search(tagname):
    '''
    generate a JSON list of dicts, one per match
    '''
    return '' #self._mock_handler(mocks.match_search)
    
@APP.route('/file/<path:file_path>')
def file_info(file_path):
    '''
    generate a JSON object describing a single file
    '''
    return '' #self._mock_handler(mocks.file_info)

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--interface', default=HOST, help='Interface to bind')
    parser.add_argument('--port', default=PORT, help='Port on which to listen')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    return parser.parse_args()

def main():
    args = parse_args()
    APP.run(host=args.interface, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
