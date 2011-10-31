import json
from webob import Response 

# todo: turn into a decorator
def _json_response(obj):
    '''
    build a response, given a function
    '''
    resp = Response(
        body=json.dumps(obj)
    )
    return resp
        
def list_tags(db):
    with db:
        cursor = db.execute('select name from tags order by name asc')
    return _json_response(cursor.fetchall())
