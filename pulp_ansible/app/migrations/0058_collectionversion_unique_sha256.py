# Generated by Django 3.2.14 on 2022-07-21 23:05

from django.db import migrations, models
from pulpcore.plugin.migrations import RequireVersion


class Migration(migrations.Migration):

    dependencies = [
        ('ansible', '0057_collectionversion_sha256_migrate'),
        ('core', '0110_apiappstatus'),
    ]

    operations = [
        # TODO adjust this version!!!
        RequireVersion("ansible", "0.22.0"),
        migrations.AlterField(
            model_name='collectionversion',
            name='sha256',
            field=models.CharField(db_index=True, max_length=64, null=False),
        ),
        migrations.AlterUniqueTogether(
            name='collectionversion',
            unique_together={('sha256',)},
        ),
    ]