__all__ = ['setup', 'get_db']

from modelplus.store import redis_db, sqlite_db

store = None

def setup(params):
    """
        'redis'   : { host, port, db }
        'sqlite'  : { file }
        'mysql'   : { host, port, db }
        'riak'    : { host, port, bucket }
        'mongodb' : { host, port, bucket }
    """
    global store

    kwargs = params.get('redis')
    if kwargs:
        store = redis_db.setup(**kwargs)
    kwargs = params.get('sqlite')
    if kwargs:
        store = sqlite_db.setup(**kwargs)

def get_db():
    return store
