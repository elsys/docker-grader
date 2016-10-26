# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20161022_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasksubmission',
            name='grade',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='tasklog',
            name='action',
            field=models.CharField(choices=[('SUBMITTED', 'Submitted'), ('CANCELED', 'Canceled'), ('STEP_COMPLETED', 'Step completed'), ('STEP_FAILED', 'Step failed')], max_length=15),
        ),
    ]
