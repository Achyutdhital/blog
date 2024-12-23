from datetime import timedelta
from django.utils import timezone 
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from .models import Post, Category, Tag
from django.db.models import Q


class IndexView(TemplateView):
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch featured posts/done
        context['featured_posts'] = Post.objects.filter(
            status='published', 
            is_featured=True
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')[:5]
        
        # Fetch recent posts/done
        context['recent_posts'] = Post.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')[:5]
        
        # Fetch popular posts/done
        context['popular_posts'] = Post.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-views_count')[:5]
        
        # Fetch posts by date
        context['posts_by_date'] = Post.objects.filter(
            status='published'
        ).dates('published_date', 'month', order='DESC')
        
        # Fetch latest post from each category
        categories = Category.objects.all()
        latest_category_posts = []
        
        for category in categories:
            latest_post = Post.objects.filter(
                category=category,
                status='published',
                published_date__isnull=False  # Ensure post is actually published
            ).select_related('author', 'category').first()
            
            if latest_post:
                post_data = {
                    'category_name': category.name,
                    'category_slug': category.slug,
                    'post': {
                        'title': latest_post.title,
                        'slug': latest_post.slug,
                        'featured_image': latest_post.featured_image,
                        'image_alt_text': latest_post.image_alt_text,
                        'published_date': latest_post.published_date,
                        'reading_time': latest_post.reading_time,
                        'author': latest_post.author,
                        'views_count': latest_post.views_count
                    }
                }
                latest_category_posts.append(post_data)
        
        context['latest_category_posts'] = latest_category_posts
        
        # Fetch categories
        categories = Category.objects.all()
        context['categories'] = categories

        # Create a list of categories with their posts
        categories_with_posts = []
        for category in categories:
            posts = Post.objects.filter(
                category=category, status='published'
            ).select_related('author', 'category').order_by('-published_date')[:5]
            categories_with_posts.append({
                'category': category,
                'posts': posts,
            })

        context['categories_with_posts'] = categories_with_posts

         # Fetch all published posts
        context['all_published_posts'] = Post.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')
        

        # Trending posts - modified query
        seven_days_ago = timezone.now() - timedelta(days=7)
        trending_posts = Post.objects.filter(
            status='published',
            published_date__gte=seven_days_ago,
            views_count__gt=0  # Only include posts with views
        ).select_related(
            'author', 
            'category'
        ).prefetch_related(
            'tags'
        ).order_by(
            '-trending_score',
            '-views_count'  # Secondary sorting by views
        )[:5]
        
        context['trending_posts'] = trending_posts

        return context



class CategoryDetailView(DetailView):
    model = Category
    template_name = 'app/category_detail.html'
    context_object_name = 'category'

    def get_object(self):
        slug = self.kwargs.get('slug')
        if slug in ['popular', 'latest']:
            return None  # Special case for "popular" and "latest" sections
        return get_object_or_404(Category, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        tag_slug = self.request.GET.get('tag')
        
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            context['posts'] = Post.objects.filter(
                tags=tag,
                category=category,
                status='published'
            ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')
            context['selected_tag'] = tag
        elif category:
            context['posts'] = Post.objects.filter(
                category=category, status='published'
            ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')
        else:
            if self.kwargs.get('slug') == 'popular':
                context['posts'] = Post.objects.filter(
                    status='published'
                ).select_related('author', 'category').prefetch_related('tags').order_by('-views_count')[:10]  # Show top 10 most popular posts
                context['category'] = {'name': 'Popular'}  # Set a default category name for display
            elif self.kwargs.get('slug') == 'latest':
                context['posts'] = Post.objects.filter(
                    status='published'
                ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')[:10]  # Show top 10 latest posts
                context['category'] = {'name': 'Latest'}  # Set a default category name for display
        
        context['categories'] = Category.objects.all()
        context['recent_posts'] = Post.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')[:5]
        context['popular_tags'] = Tag.objects.all()  # Ensure Tag is defined and imported
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'app/post_detail.html'
    context_object_name = 'post'


class PostsByDateView(ListView):
    model = Post
    template_name = 'app/posts_by_date.html'
    context_object_name = 'posts'

    def get_queryset(self):
        year = self.kwargs['year']
        month = self.kwargs['month']
        return Post.objects.filter(status='published', published_date__year=year, published_date__month=month).order_by('-published_date')