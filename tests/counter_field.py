import base
from modelplus import models

class Post(models.Model):
    title = models.StringField()
    body = models.StringField(indexed=False)
    liked = models.Counter()

class CounterTestCase(base.BaseTestCase):

    def test_basic(self):
        post = Post.objects.create(title="First!",
                body="Lorem ipsum")
        self.assert_(post)
        post.incr('liked')
        post.incr('liked', 2)
        post = Post.objects.get_by_id(post.id)
        self.assertEqual(3, post.liked)
        post.decr('liked', 2)
        post = Post.objects.get_by_id(post.id)
        self.assertEqual(1, post.liked)
