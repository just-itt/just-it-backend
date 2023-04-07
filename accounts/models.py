from django.db import models


class EmailAuth(models.Model):
    email = models.EmailField()
    auth_code = models.CharField(max_length=8)
    expire_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
