import redis

client = None

class RedisStore(object):
    def __init__(self, host='localhost', port=6379, db=1):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get_all(self, prefix):
        """Get all of the keys for a Model"""
        return [k[len(prefix)+1:] for k in self.client.keys("%s:*" % prefix)]

    def exists(self, id):
        """True if object exists"""
        return self.client.exists(id)

    def hgetall(self, key):
        """Get all of the values for a key"""
        return self.client.hgetall(key)

    def pipeline(self):
        """TODO - Transactions"""
        return self.client.pipeline()

    def counter_get(self, key, name):
        """Used by counters to get the current value"""
        return self.client.hget(key, name)

    def incr_by(self, key, name, val):
        """Increment a counter by a set amount"""
        return self.client.hincrby(key, name, val)

    def flushdb(self):
        self.client.flushdb()

    def construct(self, table):
        pass

def setup(**kwargs):
    return RedisStore(**kwargs)
