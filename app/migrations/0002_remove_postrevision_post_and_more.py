# Generated by Django 5.1.4 on 2024-12-18 04:36

import ckeditor_uploader.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postrevision',
            name='post',
        ),
        migrations.RemoveField(
            model_name='postrevision',
            name='updated_by',
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={},
        ),
        migrations.RemoveIndex(
            model_name='post',
            name='app_post_publish_7078a4_idx',
        ),
        migrations.RemoveField(
            model_name='category',
            name='canonical_url',
        ),
        migrations.RemoveField(
            model_name='category',
            name='meta_description',
        ),
        migrations.RemoveField(
            model_name='category',
            name='meta_keywords',
        ),
        migrations.RemoveField(
            model_name='category',
            name='meta_title',
        ),
        migrations.RemoveField(
            model_name='internallink',
            name='anchor_text',
        ),
        migrations.RemoveField(
            model_name='post',
            name='excerpt',
        ),
        migrations.RemoveField(
            model_name='post',
            name='meta_keywords',
        ),
        migrations.RemoveField(
            model_name='post',
            name='og_description',
        ),
        migrations.RemoveField(
            model_name='post',
            name='og_title',
        ),
        migrations.RemoveField(
            model_name='post',
            name='related_posts',
        ),
        migrations.RemoveField(
            model_name='post',
            name='twitter_card_type',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='created_at',
        ),
        migrations.AlterField(
            model_name='post',
            name='canonical_url',
            field=models.URLField(blank=True, help_text='Canonical URL if different from current URL'),
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='app.category'),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='post',
            name='featured_image',
            field=models.ImageField(blank=True, null=True, upload_to='blog/featured_images/'),
        ),
        migrations.AlterField(
            model_name='post',
            name='focus_keyword',
            field=models.CharField(blank=True, help_text='Main keyword for SEO optimization', max_length=100),
        ),
        migrations.AlterField(
            model_name='post',
            name='meta_description',
            field=models.CharField(blank=True, help_text='SEO description (max 160 characters)', max_length=160),
        ),
        migrations.AlterField(
            model_name='post',
            name='meta_title',
            field=models.CharField(blank=True, help_text='SEO title (max 60 characters)', max_length=60),
        ),
        migrations.AlterField(
            model_name='post',
            name='og_image',
            field=models.ImageField(blank=True, help_text='Image for social media sharing', null=True, upload_to='blog/og_images/'),
        ),
        migrations.AlterField(
            model_name='post',
            name='published_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='posts', to='app.tag'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['slug'], name='app_categor_slug_0ace88_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['-published_date'], name='app_post_publish_a46027_idx'),
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(fields=['slug'], name='app_tag_slug_1b0ea8_idx'),
        ),
        migrations.DeleteModel(
            name='PostRevision',
        ),
    ]
