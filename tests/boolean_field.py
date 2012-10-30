import base
from modelplus import models

class Task(models.Model):
    name = models.StringField()
    done = models.BooleanField()

class BooleanFieldTestCase(base.BaseTestCase):
    def test_CharField(self):
        t = Task(name="Cook dinner", done=False)
        assert t.save()
        self.assertFalse(t.done)

    def test_saved_CharField(self):
        t = Task(name="Cook dinner", done=False)
        assert t.save()

        t = Task.objects.all()[0]
        self.assertFalse(t.done)
        t.done = True
        assert t.save()

        t = Task.objects.all()[0]
        self.assertTrue(t.done)

    def test_indexing(self):
        assert Task.objects.create(name="Study Lua", done=False)
        assert Task.objects.create(name="Read News", done=True)
        assert Task.objects.create(name="Buy Dinner", done=False)
        assert Task.objects.create(name="Visit Sick Friend", done=False)
        assert Task.objects.create(name="Play", done=True)
        assert Task.objects.create(name="Sing a song", done=False)
        assert Task.objects.create(name="Pass the Exam", done=True)
        assert Task.objects.create(name="Dance", done=False)
        assert Task.objects.create(name="Code", done=True)
        done = Task.objects.filter(done=True)
        unfin = Task.objects.filter(done=False)
        self.assertEqual(4, len(done))
        self.assertEqual(5, len(unfin))
