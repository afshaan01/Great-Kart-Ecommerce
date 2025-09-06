from .models import Category

def categories(request):
    categories=Category.objects.all()
    return dict(cat=categories)
    