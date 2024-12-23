

# admin.py
from django.contrib import admin
from .models import Post, Category, Tag, InternalLink,Aboutus
from django.utils.html import format_html

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'display_seo_score', 'category', 'published_date', 'views_count')
    list_filter = ('status', 'category', 'created_date', 'published_date')
    search_fields = ('title', 'content', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Content', {
            'fields': (
                'title', 'slug', 'content', 'author', 'status',
                'category', 'tags', 'is_featured'
            )
        }),
        ('Images', {
            'fields': (
                'featured_image', 'og_image', 'image_alt_text',
                'lazy_loading'
            )
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': (
                'meta_title', 'meta_description', 'focus_keyword',
                'secondary_keywords', 'canonical_url', 'meta_robots',
                'structured_data'
            ),
        }),
        ('Social Media', {
            'classes': ('collapse',),
            'fields': (
                'og_type', 'twitter_card_type'
            ),
        }),
        ('Metrics', {
            'classes': ('collapse',),
            'fields': (
                ('seo_score', 'readability_score'),
                ('word_count', 'reading_time'),
                'views_count',
                'trending_score'
            ),
        }),
        ('Dates', {
            'fields': (
                'published_date',
            ),
        }),
    )

    readonly_fields = (
        'seo_score', 'readability_score', 'word_count',
        'reading_time', 'views_count', 'trending_score'
    )

    def display_seo_score(self, obj):
        """Display SEO score with color coding"""
        if obj.seo_score >= 80:
            color = 'green'
        elif obj.seo_score >= 50:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            f'{obj.seo_score}/100'
        )
    display_seo_score.short_description = 'SEO Score'

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(InternalLink)
class InternalLinkAdmin(admin.ModelAdmin):
    list_display = ('source_post', 'target_post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('source_post__title', 'target_post__title')
    autocomplete_fields = ['source_post', 'target_post']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('source_post', 'target_post', 'created_at')
        return ('created_at',)

@admin.register(Aboutus)
class Aboutusadmin(admin.ModelAdmin):
    list_display = ('company_name', 'phone_number', 'email')