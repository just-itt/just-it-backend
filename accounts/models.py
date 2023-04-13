from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailAuth(models.Model):
    class EmailAuthType(models.TextChoices):
        JOIN = "JOIN", _("JOIN")
        PASSWORD = "PASSWORD", _("PASSWORD")

    email = models.EmailField()
    auth_code = models.CharField(max_length=8)
    expire_at = models.DateTimeField()
    type = models.CharField(
        max_length=12, choices=EmailAuthType.choices, default=EmailAuthType.JOIN
    )
    created_at = models.DateTimeField(auto_now_add=True)
