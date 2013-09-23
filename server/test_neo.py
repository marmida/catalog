import mocks
import neo4j

# create the database
self.db = neo4j.GraphDatabase(self._get_db_path())

# populate the db with mock data
mocks.populate_db(self.db)
