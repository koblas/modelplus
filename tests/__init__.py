import os
import modelplus
import unittest

REDIS_DB   = int(os.environ.get('REDIS_DB', 10)) # WARNING TESTS FLUSHDB!!!
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6380))
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

if True:
    modelplus.setup({
         'sqlite' : {
            'file' : ':memory:'
         }
    })

if False:
    modelplus.setup({
        'redis' : {
            'host' : REDIS_HOST,
            'port' : REDIS_PORT,
            'db'   : REDIS_DB,
        }
    })

def all_tests():
    suite = unittest.TestSuite()

    suite.addTests(unittest.defaultTestLoader.loadTestsFromName('tests.core_tests'))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromName('tests.counter_field'))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromName('tests.boolean_field'))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromName('tests.string_field'))

    return suite

if __name__ == '__main__':
    unittest.main()
