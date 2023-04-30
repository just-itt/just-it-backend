# Generated by Django 3.2.18 on 2023-04-30 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_alter_member_profile_image'),
        ('posts', '0002_auto_20230425_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='bookmarks',
            field=models.ManyToManyField(related_name='bookmarks', to='members.Member'),
        ),
    ]
