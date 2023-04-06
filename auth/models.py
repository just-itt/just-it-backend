from django.db import models


class Email(models.Model):
    email = models.EmailField()
    auth_code = models.CharField(max_length=8)
    is_certified = models.BooleanField(default=False)
    expire_at = models.DateTimeField()
    certified_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
