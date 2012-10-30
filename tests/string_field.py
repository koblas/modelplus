import base
from modelplus import models

class Person(models.Model):
    name = models.StringField(max_length=20, required=True)

class StringFieldTestCase(base.BaseTestCase):
    def test_max_length(self):

        p = Person(name='The quick brown fox jumps over the lazy dog.')

        self.assertFalse(p.is_valid())
        self.assert_(('name', 'exceeds max length') in p.errors)
