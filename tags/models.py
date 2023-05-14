from django.db import models

from members.models import Member


class Tag(models.Model):
    title = models.CharField(max_length=64)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Option(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Customization(models.Model):
    title = models.CharField(max_length=64)
    tag_options = models.ManyToManyField(Option)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
