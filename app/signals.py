from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
import json

@receiver(post_save, sender=Post)
def generate_structured_data(sender, instance, created, **kwargs):
    if instance.status == 'published':
        structured_data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": instance.title,
            "datePublished": instance.published_date.isoformat(),
            "dateModified": instance.updated_date.isoformat(),
            "author": {
                "@type": "Person",
                "name": instance.author.get_full_name() or instance.author.username
            },
            "description": instance.meta_description
        }
        
        if instance.featured_image:
            structured_data["image"] = instance.featured_image.url

        instance.structured_data = structured_data
        Post.objects.filter(id=instance.id).update(structured_data=structured_data)
