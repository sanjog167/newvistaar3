from distutils.util import subst_vars
from unicodedata import category
from products.models import Category,Products
from django.db.models import Count,Min,Max

def extras(request):
    fcategories = Category.objects.filter(featured=True).order_by("id")
    all_cat = Category.objects.all()
    allcategories = Category.objects.annotate(num_products=Count('products'))
    minmaxprice = Products.objects.aggregate(Min('price'),Max('price'))

    return {'nav_categories':fcategories,'all_cat':all_cat,'minmaxprice':minmaxprice}