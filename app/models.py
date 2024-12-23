from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
import readability
from django.utils.html import strip_tags


class SEOModel(models.Model):
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title (max 60 characters)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description (max 160 characters)")
    canonical_url = models.URLField(blank=True, help_text="Canonical URL if different from current URL")
    focus_keyword = models.CharField(max_length=100, blank=True, help_text="Main keyword for SEO optimization")
    structured_data = models.JSONField(default=dict, blank=True, help_text="Schema.org structured data")
    secondary_keywords = models.CharField(max_length=200, blank=True, help_text="Comma-separated secondary keywords")
    meta_robots = models.CharField(
        max_length=50,
        default="index, follow",
        help_text="Robot meta tag instructions"
    )
    og_type = models.CharField(
        max_length=50,
        default="article",
        help_text="Open Graph type"
    )
    twitter_card_type = models.CharField(
        max_length=50,
        default="summary_large_image",
        help_text="Twitter card type"
    )

    class Meta:
        abstract = True

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"
        indexes = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        indexes = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})

class Post(SEOModel):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    # Basic Fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=75, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = RichTextUploadingField()
    featured_image = models.ImageField(upload_to='blog/featured_images/', blank=True, null=True)
    og_image = models.ImageField(upload_to='blog/og_images/', blank=True, null=True, help_text="Image for social media sharing")
    image_alt_text = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True)
    
    # Analytics fields
    views_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=0, help_text="Estimated reading time in minutes")
    word_count = models.PositiveIntegerField(default=0)
    seo_score = models.PositiveIntegerField(default=0, editable=False)

    # New SEO and Performance fields
    lazy_loading = models.BooleanField(default=True, help_text="Enable lazy loading for images")
    image_optimization = models.JSONField(
        default=dict,
        help_text="Store image optimization metadata"
    )
    cache_ttl = models.PositiveIntegerField(
        default=3600,
        help_text="Cache time-to-live in seconds"
    )
    readability_score = models.FloatField(default=0, help_text="Flesch Reading Ease score")
    heading_structure_valid = models.BooleanField(default=False)
    trending_score = models.FloatField(default=0)
    last_view_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-published_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        # Set published date when status changes to published
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()

        # Generate meta description if not provided
        if not self.meta_description and self.content:
            plain_content = BeautifulSoup(self.content, 'html.parser').get_text()
            self.meta_description = plain_content[:157] + "..." if len(plain_content) > 157 else plain_content

        # Generate meta title if not provided
        if not self.meta_title:
            self.meta_title = self.title[:60]

        # Calculate metrics
        self._calculate_metrics()
        
        # Save first to get ID if needed
        super().save(*args, **kwargs)
        
        # Generate and save structured data
        self.structured_data = self.generate_structured_data()
        super().save(*args, **kwargs)

    def _calculate_metrics(self):
        """Calculate various metrics for the post"""
        plain_content = BeautifulSoup(self.content, 'html.parser').get_text()
        
        # Calculate basic metrics
        self.word_count = len(plain_content.split())
        self.reading_time = max(1, round(self.word_count / 200))
        
        # Calculate SEO and readability scores
        self.seo_score = self.check_seo_score()
        self.readability_score = self._calculate_readability()
        self.heading_structure_valid = self._check_heading_structure()

    def check_seo_score(self):
        """Calculate SEO score based on various factors"""
        score = 0
        checks = {
            'title_length': {
                'check': 45 <= len(self.title) <= 60,
                'weight': 10
            },
            'meta_description_length': {
                'check': 145 <= len(self.meta_description) <= 160,
                'weight': 10
            },
            'keyword_in_title': {
                'check': self.focus_keyword.lower() in self.title.lower() if self.focus_keyword else False,
                'weight': 15
            },
            'keyword_in_meta_description': {
                'check': self.focus_keyword.lower() in self.meta_description.lower() if self.focus_keyword else False,
                'weight': 10
            },
            'image_optimization': {
                'check': bool(self.featured_image and self.image_alt_text),
                'weight': 10
            },
            'content_length': {
                'check': self.word_count >= 1500,
                'weight': 15
            },
            'keyword_density': {
                'check': self._check_keyword_density(),
                'weight': 10
            },
            'structured_data': {
                'check': bool(self.structured_data),
                'weight': 10
            },
            'heading_structure': {
                'check': self.heading_structure_valid,
                'weight': 10
            }
        }

        for check, data in checks.items():
            if data['check']:
                score += data['weight']

        return score

    def _check_keyword_density(self):
        """Check if keyword density is between 1-3%"""
        if not self.focus_keyword:
            return False
        
        text = BeautifulSoup(self.content, 'html.parser').get_text()
        word_count = len(text.split())
        keyword_count = text.lower().count(self.focus_keyword.lower())
        density = (keyword_count / word_count) * 100
        return 1 <= density <= 3

    def _calculate_readability(self):
        """Calculate Flesch Reading Ease score"""
        text = BeautifulSoup(self.content, 'html.parser').get_text()
        try:
            return readability.flesch_kincaid_grade(text)
        except:
            return 0

    def _check_heading_structure(self):
        """Validate heading structure (H1-H6)"""
        soup = BeautifulSoup(self.content, 'html.parser')
        headings = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        found_headings = [h.name for h in soup.find_all(headings)]
        
        if not found_headings:
            return False

        # Check if headings are in correct order
        return all(int(found_headings[i][1]) <= int(found_headings[i+1][1]) 
                  for i in range(len(found_headings)-1))

    def increment_view(self):
        """Increment view count and update trending score"""
        self.views_count += 1
        self.last_view_date = timezone.now()
        self.calculate_trending_score()
        self.save()

    def calculate_trending_score(self):
        """Calculate trending score based on views and time decay"""
        now = timezone.now()
        time_window = now - timedelta(days=7)
        
        if self.last_view_date:
            time_diff = now - self.last_view_date
            hours_passed = time_diff.total_seconds() / 3600.0
            time_decay = 1.0 / (1 + hours_passed/24)
            self.trending_score = self.views_count * time_decay
        else:
            self.trending_score = 0

    def get_absolute_url(self):
        """Get the absolute URL for the post"""
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def generate_structured_data(self):
        """Generate Schema.org structured data"""
        structured_data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": self.title,
            "datePublished": self.published_date.isoformat() if self.published_date else None,
            "dateModified": self.updated_date.isoformat() if self.updated_date else None,
            "author": {
                "@type": "Person",
                "name": self.author.get_full_name() or self.author.username
            },
            "description": self.meta_description,
            "wordCount": self.word_count,
            "articleBody": BeautifulSoup(self.content, 'html.parser').get_text()
        }

        if self.featured_image:
            structured_data["image"] = {
                "@type": "ImageObject",
                "url": self.featured_image.url,
                "alt": self.image_alt_text
            }

        if self.category:
            structured_data["articleSection"] = self.category.name

        if self.tags.exists():
            structured_data["keywords"] = ", ".join([tag.name for tag in self.tags.all()])

        return structured_data

    def get_social_meta(self):
        """Get social media metadata"""
        return {
            'twitter': {
                'card': self.twitter_card_type,
                'title': self.meta_title[:60],
                'description': self.meta_description[:200],
                'image': self.og_image.url if self.og_image else self.featured_image.url if self.featured_image else None,
            },
            'facebook': {
                'og_type': self.og_type,
                'title': self.meta_title[:60],
                'description': self.meta_description[:200],
                'image': self.og_image.url if self.og_image else self.featured_image.url if self.featured_image else None,
            }
        }

class InternalLink(models.Model):
    source_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='outbound_links')
    target_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='inbound_links')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['source_post', 'target_post']

    def __str__(self):
        return f"Link from {self.source_post.title} to {self.target_post.title}"


class Aboutus(models.Model):
    company_name = models.CharField(max_length=255)
    address = models.TextField()
    logo = models.ImageField(upload_to='blog/aboutus/logos/')
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    map_location = models.URLField(blank=True, null=True)  # or use a geolocation field like models.PointField()
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    # Add more fields as needed

    def save(self, *args, **kwargs):
        if Aboutus.objects.exists() and not self.pk:
            raise ValidationError("Only one 'About Us' entry is allowed. You can only edit the existing entry.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name