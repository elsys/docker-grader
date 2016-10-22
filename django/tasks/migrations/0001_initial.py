# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date', models.DateTimeField(editable=False, default=django.utils.timezone.now)),
                ('action', models.CharField(choices=[('SUBMIT', 'Submit'), ('CANCEL', 'Canel')], max_length=15)),
                ('extra', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TaskStep',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('task', models.ForeignKey(related_name='steps', to='tasks.Task')),
            ],
        ),
        migrations.CreateModel(
            name='TaskSubmission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('task', models.ForeignKey(related_name='submissions', to='tasks.Task')),
                ('user', models.ForeignKey(related_name='submissions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='tasklog',
            name='task_submission',
            field=models.ForeignKey(related_name='log', to='tasks.TaskSubmission'),
        ),
    ]
