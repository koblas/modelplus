import json
import sqlite3

class Transaction(object):
    def __init__(self, store):
        self.store = store
        self.cursor = store.connection.cursor()
        self.stmts  = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return

    def delete(self, key):
        table, id = key.split(':')
        self.store.construct(table)
        self.stmts.append(["DELETE FROM %s WHERE id = ?" % table, [id]])

    def hmset(self, key, hash):
        table, id = key.split(':')
        self.store.construct(table)
        self.stmts.append(["INSERT OR REPLACE INTO %s (id, blob) VALUES (?, ?)" % table, [id, json.dumps(hash)]])

    def execute(self):
        for stmt in self.stmts:
            self.cursor.execute(*stmt)
        self.stmts = []

class SqliteStore(object):
    inited = set()

    def __init__(self, file=None):
        self.connection = sqlite3.connect(file)

    def get_all(self, prefix):
        """Get all of the keys for a Model"""
        #return self.connection.keys("%s*" % prefix)
        cursor = self.connection.cursor()
        return [row[0] for row in cursor.execute("SELECT id FROM %s" % prefix)]

    def exists(self, key):
        """True if object exists"""
        table, id = key.split(':')
        cursor = self.connection.cursor()
        return bool([row[0] for row in cursor.execute("SELECT id FROM %s WHERE id = ?" % table, [id])])

    def hgetall(self, key):
        """Get all of the values for a key"""
        table, id = key.split(':')
        cursor = self.connection.cursor()
        for row in cursor.execute("SELECT blob FROM %s WHERE id = ?" % table, [id]):
            return json.loads(row[0])
        return None

    def pipeline(self):
        """TODO - Transactions"""
        return Transaction(self)

    def counter_get(self, key, name):
        """Used by counters to get the current value"""
        data = self.hgetall(key)
        if data:
            return data.get(name, 0) 
        return None

    def incr_by(self, key, name, val):
        """Increment a counter by a set amount"""
        data = self.hgetall(key)

        if data:
            data[name] = str(int(data.get(name, 0)) + val)

            with self.pipeline() as pipeline:
                pipeline.hmset(key, data)
                pipeline.execute()

    def flushdb(self):
        """Delete all of the tables..."""
        cursor = self.connection.cursor()
        for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            cursor.execute("DROP TABLE %s" % row[0])
        self.inited = set()

    def construct(self, table):
        """Insure that the table is created before we start operating on it"""
        if table in self.inited:
            return
        self.inited.add(table)

        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS %s (id TEXT PRIMARY KEY, blob TEXT)" % table)

def setup(**kwargs):
    return SqliteStore(**kwargs)
