# middleware.py
from django.utils import timezone

class PostViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if this is a post detail view
        if hasattr(request, 'resolver_match') and request.resolver_match:
            if request.resolver_match.url_name == 'post_detail':
                post = request.resolver_match.func.view_class.get_object(
                    request.resolver_match.func.view_class(
                        object=None, 
                        kwargs=request.resolver_match.kwargs
                    )
                )
                # Increment view count
                post.views_count += 1
                # Update trending score
                post.calculate_trending_score()
                post.save()
        
        return response
