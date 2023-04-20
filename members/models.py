from django.db import models
from django.utils.translation import gettext_lazy as _


class Member(models.Model):
    class MemberStatus(models.TextChoices):
        ACTIVE = "ACTIVE", _("ACTIVE")
        WITHDRAW = "WITHDRAW", _("WITHDRAW")

    email = models.EmailField()
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=128)
    profile_image = models.FilePathField(null=True)
    status = models.CharField(
        max_length=12, choices=MemberStatus.choices, default=MemberStatus.ACTIVE
    )
    last_login_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
