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
    with db.transaction:
        tag_root_node = db.reference_node.TAGS.single.endNode
        result = [tag_rel.endNode['name'] for tag_rel in tag_root_node.IS_TAG]
    
    return _json_response(result)
