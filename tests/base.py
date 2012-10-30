import unittest
import modelplus

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = modelplus.get_db()
        self.client.flushdb()

    def tearDown(self):
        self.client.flushdb()
