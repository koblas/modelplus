# -*- coding: utf-8 -*-

import base
from datetime import datetime
from modelplus import models

class Person(models.Model):
    class Meta:
        indices = ['full_name']

    first_name = models.StringField()
    last_name  = models.StringField()
    created_at = models.DateTimeField(default=datetime.now)

    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name,)

#
#
#
class ModelTestCase(base.BaseTestCase):
    def test_save(self):
        p1 = Person(first_name="Granny", last_name="Goose")
        p2 = Person(first_name="George", last_name="Jetson")
        p1.save()
        p2.save()

        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertNotEqual(p1.id, p2.id)

    def test_fields(self):
        obj = Person(first_name="Granny", last_name="Goose")

        self.assertEqual("Granny", obj.first_name)
        self.assertEqual("Goose", obj.last_name)
        self.assertIsInstance(obj.created_at, datetime)

        self.assertIsNotNone(obj.created_at)

    def test_is_new(self):
        obj = Person(first_name="Darken", last_name="Rahl")
        self.assertTrue(obj.is_new())

    def test_update(self):
        obj = Person(first_name="Granny", last_name="Goose")
        obj.save()

        p = Person.objects.get_by_id(obj.id)
        p.first_name = "Morgan"
        p.last_name = None
        assert p.save()

        p = Person.objects.get_by_id(p.id)
        self.assertEqual("Morgan", p.first_name)
        self.assertEqual(None, p.last_name)

    def test_all(self):
        p1 = Person(first_name="Granny", last_name="Goose")
        p1.save()
        p2 = Person(first_name="Jejomar", last_name="Binay")
        p2.save()

        all = Person.objects.all().order('created_at')
        self.assertEqual([p1, p2], list(all))

    def test_unicode(self):
        p = Person(first_name=u"Niña", last_name="Jose")
        self.assert_(p.save())
        g = Person.objects.create(first_name="Granny", last_name="Goose")
        self.assert_(g)

        p = Person.objects.filter(first_name=u"Niña").first()
        self.assert_(p)
        self.assert_(isinstance(p.full_name(), unicode))
        self.assertEqual(u"Niña Jose", p.full_name())

    def test_getitem(self):
        person1 = Person(first_name="Granny", last_name="Goose")
        person1.save()
        person2 = Person(first_name="Jejomar", last_name="Binay")
        person2.save()

        p1 = Person.objects.get_by_id(person1.id)
        p2 = Person.objects.get_by_id(person2.id)

        self.assertEqual('Jejomar', p2.first_name)
        self.assertEqual('Binay', p2.last_name)

        self.assertEqual('Granny', p1.first_name)
        self.assertEqual('Goose', p1.last_name)

    def test_manager_create(self):
        person = Person.objects.create(first_name="Granny", last_name="Goose")

        p1 = Person.objects.get_by_id(person.id)
        self.assertEqual('Granny', p1.first_name)
        self.assertEqual('Goose', p1.last_name)

    def test_delete(self):
        Person.objects.create(first_name="Granny", last_name="Goose")
        Person.objects.create(first_name="Clark", last_name="Kent")
        Person.objects.create(first_name="Granny", last_name="Mommy")
        Person.objects.create(first_name="Granny", last_name="Kent")

        for p in Person.objects.all():
            p.delete()

        self.assertEqual(0, len(Person.objects.all()))

    def test_filter(self):
        Person.objects.create(first_name="Granny", last_name="Goose")
        Person.objects.create(first_name="Clark", last_name="Kent")
        Person.objects.create(first_name="Granny", last_name="Mommy")
        Person.objects.create(first_name="Granny", last_name="Kent")
        persons = Person.objects.filter(first_name="Granny")

        self.assertEqual(3, len(persons))

        persons = Person.objects.filter(first_name="Clark")
        self.assertEqual(1, len(persons))

        # by index
        persons = Person.objects.filter(full_name="Granny Mommy")
        self.assertEqual(1, len(persons))
        self.assertEqual("Granny Mommy", persons[0].full_name())

    def test_exclude(self):
        Person.objects.create(first_name="Granny", last_name="Goose")
        Person.objects.create(first_name="Clark", last_name="Kent")
        Person.objects.create(first_name="Granny", last_name="Mommy")
        Person.objects.create(first_name="Granny", last_name="Kent")
        persons = Person.objects.exclude(first_name="Granny")

        self.assertEqual(1, len(persons))

        persons = Person.objects.exclude(first_name="Clark")
        self.assertEqual(3, len(persons))

        # by index
        persons = Person.objects.exclude(full_name="Granny Mommy").order('created_at')
        self.assertEqual(3, len(persons))
        self.assertEqual("Granny Goose", persons[0].full_name())
        self.assertEqual("Clark Kent", persons[1].full_name())
        self.assertEqual("Granny Kent", persons[2].full_name())

        # mixed
        Person.objects.create(first_name="Granny", last_name="Pacman")
        persons = (Person.objects.filter(first_name="Granny").exclude(last_name="Mommy"))
        self.assertEqual(3, len(persons))

    def test_first(self):
        p = Person.objects.create(first_name="Granny", last_name="Goose")
        Person.objects.create(first_name="Clark", last_name="Kent")
        Person.objects.create(first_name="Granny", last_name="Mommy")
        Person.objects.create(first_name="Granny", last_name="Kent")
        granny = Person.objects.filter(first_name="Granny").order('created_at').first()
        self.assertEqual(p.id, granny.id)
        lana = Person.objects.filter(first_name="Lana").first()
        self.assertFalse(lana)

    def test_iter(self):
        Person.objects.create(first_name="Granny", last_name="Goose")
        Person.objects.create(first_name="Clark", last_name="Kent")
        Person.objects.create(first_name="Granny", last_name="Mommy")
        Person.objects.create(first_name="Granny", last_name="Kent")

        for person in Person.objects.all():
            self.assertTrue(person.full_name() in ("Granny Goose", "Clark Kent", "Granny Mommy", "Granny Kent"))
