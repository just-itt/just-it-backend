# Generated by Django 3.2.18 on 2023-04-13 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_member_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('WITHDRAW', 'WITHDRAW')], default='ACTIVE', max_length=12),
        ),
    ]
