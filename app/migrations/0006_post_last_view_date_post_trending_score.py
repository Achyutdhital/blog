# Generated by Django 5.1.4 on 2024-12-20 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_aboutus'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='last_view_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='trending_score',
            field=models.FloatField(default=0),
        ),
    ]
