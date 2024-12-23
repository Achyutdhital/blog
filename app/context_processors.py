from app.models import Category,Post,Aboutus

def categories_processor(request):
    about = Aboutus.objects.first()
    categories = Category.objects.all()
    primary_categories = categories[:4]
    more_categories = categories[4:]
    return {
        'primary_categories': primary_categories,
        'more_categories': more_categories,
        'about': about,
    }


