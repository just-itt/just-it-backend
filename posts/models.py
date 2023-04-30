from django.db import models

from members.models import Member
from tags.models import Option


class Post(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField()
    author = models.ForeignKey(Member, on_delete=models.CASCADE)
    bookmarks = models.ManyToManyField(Member, related_name="bookmarks")
    tag_options = models.ManyToManyField(Option)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Image(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    image = models.FilePathField()
    ratio = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
