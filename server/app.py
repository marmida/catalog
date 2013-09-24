'''
Backend web application module.  Uses flask.
'''
# This sucks, but without it, /usr/lib/python2.7/dist-packages is not
# included in sys.path, so the system-installed python-jpype package
# will not be accessible.
# See: https://groups.google.com/forum/#!topic/python-virtualenv/FBKZRYDwosY
import sys
sys.path.append('/usr/lib/python2.7/dist-packages')


from argparse import ArgumentParser
from flask import Flask
import json
import mocks
import neo4j
import os.path
import tempfile

import db

HOST = '127.0.0.1'
PORT = 8080
APP = Flask('catalog')
CLIENT_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'www'))
THE_DB = None
        
@APP.route('/tags')        
def list_tags():
    '''
    generate a JSON list of tags
    
    '''
    with THE_DB.transaction:
        tag_root_node = THE_DB.reference_node.TAGS.single.endNode
        result = [tag_rel.endNode['name'] for tag_rel in tag_root_node.IS_TAG]
    
    return json.dumps(result)

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

    global THE_DB
    THE_DB = neo4j.GraphDatabase(tempfile.mkdtemp())
    mocks.populate_db(THE_DB)

    try:
        APP.run(host=args.interface, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        pass

    THE_DB.shutdown()

if __name__ == '__main__':
    main()
