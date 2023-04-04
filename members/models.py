from django.db import models


class Member(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=128)
    profile_image = models.FileField(upload_to="uploads/%Y/%m/%d", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    last_login_at = models.DateTimeField(null=True)
