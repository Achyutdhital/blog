# Generated by Django 5.1.4 on 2024-12-21 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_delete_aboutus_post_cache_ttl_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aboutus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('logo', models.ImageField(upload_to='blog/aboutus/logos/')),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20)),
                ('map_location', models.URLField(blank=True, null=True)),
                ('facebook_url', models.URLField(blank=True, null=True)),
                ('twitter_url', models.URLField(blank=True, null=True)),
                ('instagram_url', models.URLField(blank=True, null=True)),
                ('linkedin_url', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
