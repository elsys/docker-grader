# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='docker_image',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='slug',
            field=models.SlugField(unique=True, default='', max_length=31),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskstep',
            name='input_source',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskstep',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskstep',
            name='output_source',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tasksubmission',
            name='uuid',
            field=models.UUIDField(editable=False, default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='tasksubmission',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='submissions'),
        ),
    ]
