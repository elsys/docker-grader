# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import uuid
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('slug', models.SlugField(max_length=31, unique=True)),
                ('docker_image', models.CharField(max_length=255)),
                ('description', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('date', models.DateTimeField(editable=False, default=django.utils.timezone.now)),
                ('action', models.CharField(max_length=15, choices=[('SUBMITTED', 'Submitted'), ('CANCELED', 'Canceled'), ('STEP_COMPLETED', 'Step completed'), ('STEP_FAILED', 'Step failed')])),
                ('extra', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TaskStep',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('order', models.PositiveSmallIntegerField()),
                ('input_source', models.TextField()),
                ('output_source', models.TextField()),
                ('task', models.ForeignKey(to='tasks.Task', related_name='steps')),
            ],
        ),
        migrations.CreateModel(
            name='TaskSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('uuid', models.UUIDField(editable=False, default=uuid.uuid4)),
                ('grade', models.FloatField(default=0)),
                ('task', models.ForeignKey(to='tasks.Task', related_name='submissions')),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='submissions')),
            ],
        ),
        migrations.AddField(
            model_name='tasklog',
            name='task_submission',
            field=models.ForeignKey(to='tasks.TaskSubmission', related_name='log'),
        ),
    ]
