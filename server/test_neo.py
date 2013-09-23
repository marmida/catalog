# This sucks, but without it, /usr/lib/python2.7/dist-packages is not
# included in sys.path, so the system-installed python-jpype package
# will not be accessible.
import sys
sys.path.append('/usr/lib/python2.7/dist-packages')


import mocks
import neo4j

# create the database
db = neo4j.GraphDatabase('/tmp/test')

# populate the db with mock data
mocks.populate_db(db)

db.shutdown()