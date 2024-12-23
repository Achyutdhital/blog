from django.urls import path
from .views import IndexView, CategoryDetailView, PostDetailView, PostsByDateView

app_name = 'app'  # Define the namespace

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('section/popular/', CategoryDetailView.as_view(), {'slug': 'popular'}, name='popular_section'), 
    path('section/latest/', CategoryDetailView.as_view(), {'slug': 'latest'}, name='latest_section'),  
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:year>/<int:month>/', PostsByDateView.as_view(), name='posts_by_date'),

]