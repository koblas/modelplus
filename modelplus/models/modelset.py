"""
Handles the queries.
"""
import modelplus
from exceptions import AttributeNotIndexed

# Model Set
class ModelSet(object):
    def __init__(self, model_class):
        self.model_class = model_class
        self.key = model_class._key
        # We access directly _meta as .db is a property and should be
        # access from an instance, not a Class
        self._db = model_class._meta['db'] or modelplus.get_db()
        self._filters = {}
        self._exclusions = {}
        self._ordering = []
        self._limit = None
        self._offset = None

        # Insure that we've done any necessary DB work to make this class happen
        self.db.construct(model_class._key)

    #################
    # MAGIC METHODS #
    #################

    def __getitem__(self, index):
        """
        Will look in _set to get the id and simply return the instance of the model.
        """
        if isinstance(index, slice):
            return map(lambda id: self._get_item_with_id(id), self._set[index])
        else:
            id = self._set[index]
            if id:
                return self._get_item_with_id(id)
            else:
                raise IndexError

    def __repr__(self):
        if len(self._set) > 30:
            m = self._set[:30]
        else:
            m = self._set
        s = map(lambda id: self._get_item_with_id(id), m)
        return "%s" % s

    def __iter__(self):
        for id in self._set:
            yield self._get_item_with_id(id)

    def __len__(self):
        return len(self._set)

    def __contains__(self, val):
        return val.id in self._set

    ##########################################
    # METHODS THAT RETURN A SET OF INSTANCES #
    ##########################################

    def get_by_id(self, id):
        """
        Returns the object definied by ``id``.

        :param id: the ``id`` of the objects to lookup.
        :returns: The object instance or None if not found.

        >>> from redisco import models
        >>> class Foo(models.Model):
        ...     name = models.StringField()
        ...
        >>> f = Foo(name="Einstein")
        >>> f.save()
        True
        >>> Foo.objects.get_by_id(f.id) == f
        True
        >>> [f.delete() for f in Foo.objects.all()] # doctest: +ELLIPSIS
        [...]
        """
        if (self._filters or self._exclusions) and str(id) not in self._set:
            return
        if self.model_class.exists(id):
            return self._get_item_with_id(id)

    def first(self):
        """
        Return the first object of a collections.

        :return: The object or Non if the lookup gives no result


        >>> from redisco import models
        >>> class Foo(models.Model):
        ...     name = models.StringField()
        ...
        >>> f = Foo(name="toto")
        >>> f.save()
        True
        >>> Foo.objects.filter(name="toto").first() # doctest: +ELLIPSIS
        <Foo:...>
        >>> [f.delete() for f in Foo.objects.all()] # doctest: +ELLIPSIS
        [...]
        """
        try:
            return self.limit(1).__getitem__(0)
        except IndexError:
            return None


    #####################################
    # METHODS THAT MODIFY THE MODEL SET #
    #####################################

    def filter(self, **kwargs):
        """
        Filter a collection on criteria

        >>> from redisco import models
        >>> class Foo(models.Model):
        ...     name = models.StringField()
        ...
        >>> Foo(name="toto").save()
        True
        >>> Foo(name="toto").save()
        True
        >>> Foo.objects.filter() # doctest: +ELLIPSIS
        [<Foo:...>, <Foo:...>]
        >>> [f.delete() for f in Foo.objects.all()] # doctest: +ELLIPSIS
        [...]
        """
        clone = self._clone()
        if not clone._filters:
            clone._filters = {}
        clone._filters.update(kwargs)
        return clone

    def exclude(self, **kwargs):
        """
        Exclude a collection within a lookup.


        >>> from redisco import models
        >>> class Foo(models.Model):
        ...    name = models.StringField()
        ...    exclude_me = models.BooleanField()
        ...
        >>> Foo(name="Einstein").save()
        True
        >>> Foo(name="Edison", exclude_me=True).save()
        True
        >>> Foo.objects.exclude(exclude_me=True).first().name
        u'Einstein'
        >>> [f.delete() for f in Foo.objects.all()] # doctest: +ELLIPSIS
        [...]
        """
        clone = self._clone()
        if not clone._exclusions:
            clone._exclusions = {}
        clone._exclusions.update(kwargs)
        return clone

    # this should only be called once
    def order(self, field):
        """
        Enable ordering in collections when doing a lookup.

        .. Warning:: This should only be called once per lookup.

        >>> from redisco import models
        >>> class Foo(models.Model):
        ...    name = models.StringField()
        ...    exclude_me = models.BooleanField()
        ...
        >>> Foo(name="Abba").save()
        True
        >>> Foo(name="Zztop").save()
        True
        >>> Foo.objects.all().order("-name").first().name
        u'Zztop'
        >>> Foo.objects.all().order("name").first().name
        u'Abba'
        >>> [f.delete() for f in Foo.objects.all()] # doctest: +ELLIPSIS
        [...]
        """
        fname = field.lstrip('-')
        if fname not in self.model_class._indices:
            raise ValueError("Order parameter should be an indexed attribute.")
        alpha = True
        if fname in self.model_class._attributes:
            v = self.model_class._attributes[fname]
        clone = self._clone()
        if not clone._ordering:
            clone._ordering = []
        clone._ordering.append((field, alpha,))
        return clone

    def limit(self, n, offset=0):
        """
        Limit the size of the collection to *n* elements.
        """
        clone = self._clone()
        clone._limit = n
        clone._offset = offset
        return clone

    def create(self, **kwargs):
        """
        Create an object of the class.

        .. Note:: This is the same as creating an instance of the class and saving it.

        >>> from redisco import models
        >>> class Foo(models.Model):
        ...     name = models.StringField()
        ...
        >>> Foo.objects.create(name="Obama") # doctest: +ELLIPSIS
        <Foo:...>
        >>> [f.delete() for f in Foo.objects.all()] # doctest: +ELLIPSIS
        [...]
        """
        instance = self.model_class(**kwargs)
        if instance.save():
            return instance
        else:
            return None

    def all(self):
        """
        Return all elements of the collection.
        """
        return self._clone()

    def get_or_create(self, **kwargs):
        """
        Return an element of the collection or create it if necessary.

        >>> from redisco import models
        >>> class Foo(models.Model):
        ...     name = models.StringField()
        ...
        >>> new_obj = Foo.objects.get_or_create(name="Obama")
        >>> get_obj = Foo.objects.get_or_create(name="Obama")
        >>> new_obj == get_obj
        True
        >>> [f.delete() for f in Foo.objects.all()] # doctest: +ELLIPSIS
        [...]
        """
        opts = {}
        for k, v in kwargs.iteritems():
            if k in self.model_class._indices:
                opts[k] = v
        o = self.filter(**opts).first()
        if o:
            return o
        else:
            return self.create(**kwargs)

    #

    @property
    def db(self):
        return self._db

    ###################
    # PRIVATE METHODS #
    ###################

    @property
    def _set(self):
        """
        This contains the list of ids that have been looked-up,
        filtered and ordered. This set is build hen we first access
        it and is cached for has long has the ModelSet exist.
        """
        if hasattr(self, '_cached_set'):
            return self._cached_set

        s = self.db.get_all(self.key)

        self._cached_set = []
        if self._filters or self._exclusions:
            r = []
            for obj in [self._get_item_with_id(id) for id in s]:
                if (((self._filters and self._check_filters(self._filters, obj)) or not self._filters) and
                    ((self._exclusions and not self._check_filters(self._exclusions, obj)) or not self._exclusions)):
                    r.append(obj.id)
            s = r

        self._cached_set = self._order(s, self.key)

        return self._cached_set

    def _check_filters(self, filters, obj):
        """
        Give a list of filters (name == value) check to make sure
        the given object is contained in that set.

        This should cover both "filters" and "exclusions" since we're testing correctly

        :return boolean
        """

        for k, v in filters.iteritems():
            if k not in self.model_class._indices:
                raise AttributeNotIndexed("Attribute %s is not indexed in %s class." % (k, self.model_class.__name__))

            # Handle properties
            val = getattr(obj, k)
            if callable(val):
                if val() != v:
                    return False
            elif val != v:
                return False
        return True

    def _order(self, keys, skey):
        """
        This function does not job. It will only call the good
        subfunction in case we want an ordering or not.
        """
        if self._ordering:
            return self._set_with_ordering(keys, skey)
        else:
            return self._set_without_ordering(keys, skey)

    def _set_with_ordering(self, keys, skey):
        """
        Final call for finally ordering the looked-up collection.
        The ordering will be done by Redis itself and stored as a temporary set.

        :return: a Set of `id`
        """

        num, start = self._get_limit_and_offset()

        info = []
        for ordering, alpha in self._ordering:
            if ordering.startswith('-'):
                desc = True
                ordering = ordering.lstrip('-')
            else:
                desc = False
            info.append((ordering, desc))

        objs = [self._get_item_with_id(id) for id in keys]

        def sortfunc(a, b):
            for k, desc in info:
                val = getattr(a, k)
                av = val() if callable(val) else val

                val = getattr(b, k)
                bv = val() if callable(val) else val

                v = cmp(av, bv)
                if v != 0:
                    return v
            return 0

        return [obj.id for obj in sorted(objs, cmp=sortfunc)]

    def _set_without_ordering(self, keys, skey):
        """
        Final call for "non-ordered" looked up.
        We order by id anyway.

        :returns: A Set of `id`
        """

        return sorted(keys)

    def _get_limit_and_offset(self):
        """
        Return the limit and offset of the looked up ids.
        """
        if (self._limit is not None and self._offset is None) or \
                (self._limit is None and self._offset is not None):
                    raise "Limit and offset must be specified"

        if self._limit is None:
            return (None, None)
        else:
            return (self._limit, self._offset)

    def _get_item_with_id(self, id):
        """
        Fetch an object and return the instance. The real fetching is
        done by assigning the id to the Instance. See ``Model`` class.
        """
        instance = self.model_class()
        instance.id = str(id)
        return instance

    def _clone(self):
        """
        This function allows the chaining of lookup calls.
        Example:
            Foo.objects.filter().filter().exclude()...

        :returns: a modelset instance with all the previous filters.
        """
        klass = self.__class__
        c = klass(self.model_class)
        if self._filters:
            c._filters = self._filters
        if self._exclusions:
            c._exclusions = self._exclusions
        if self._ordering:
            c._ordering = self._ordering
        c._limit = self._limit
        c._offset = self._offset
        return c
