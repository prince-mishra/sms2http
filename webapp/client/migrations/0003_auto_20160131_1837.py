# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0002_auto_20160126_1520'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sms',
            options={'ordering': ['-created']},
        ),
    ]
