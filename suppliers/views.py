from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Supplier,Company
from products.models import Products,Category
from products.views import search_algorithm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



from django.shortcuts import render

# Create your views here.
    
def all_suppliers(request):

    sup = Supplier.objects.all()

    return render(request,'supplier_detail.html',{'sup':sup})

def supplier_detail(request,id):

    
    supplier = get_object_or_404(Supplier,id=id)
    
    supplier_products = supplier.products_set.all().order_by("-clicks")[:10]
    
    all_products = supplier.products_set.all()
    
    supplier_category = []
    
    for p in all_products:
        if not p.category in supplier_category:
            supplier_category.append(p.category)


    if request.method == 'POST':
        
        success = 1
        
        # return render(request,'supplier/profile_page.html',{'success':'Success'})
        return render(request,'supplier/seller_page.html',{'success':'Success'})
        
    else:
        
        #return render(request,'supplier/seller_page.html',{'supplier':supplier,'products':supplier_products,'category':supplier_category,'all_products':all_products})
        return render(request,'supplier/seller_page.html',{'supplier':supplier,'products':supplier_products,'category':supplier_category,'all_products':all_products})

def new_supplier_detail(request,slug):
    context = {}
    if id != None:
        supplier = get_object_or_404(Supplier,slug=slug)

    if request.method == "POST" and request.user.is_authenticated:
        if "profile_picture" in request.FILES:
            supplier.profile_picture = request.FILES["profile_picture"]
            supplier.save()
            messages.add_message(request, messages.SUCCESS, 'Your profile picture has been changed successfully')

    keyword = request.GET.get("keyword")
    sort = request.GET.get("sort")
    min_value = request.GET.get("min_value")
    max_value = request.GET.get("max_value")
    if max_value == 0:
        max_value = None
    categ = request.GET.get("categ")
    sub_categ = None

    products = search_algorithm(None, sub_categ, keyword, min_value, max_value, sort, slug, _type="sellerpage")

    # First find the min-max price of all products (when not filtered with the min-max price range)
    min_price_of_all_products = 0
    max_price_of_all_products = 0
    try:
        max_price_of_all_products = products[0].price
    except:
        pass

    for p in products:
        if p.price < min_price_of_all_products:
            min_price_of_all_products = p.price
        if p.price > max_price_of_all_products:
            max_price_of_all_products = p.price

    # Now apply the min-max filter
    if min_value != None:
        products = products.filter(price__gte=min_value)
    else:
        min_value = 0
    if max_value != None:
        products = products.filter(price__lte=max_value)
    else:
        max_value = max_price_of_all_products

    context['products'] = products

    search_category = []
    for p in products:
        if not p.category in search_category:
            search_category.append(p.category)
        if p.price < min_price_of_all_products:
            min_price_of_all_products = p.price
        if p.price > max_price_of_all_products:
            max_price_of_all_products = p.price

    # Now filter by category
    if categ != None:
        products = products.filter(category__slug=categ)

    # Pagination

    pag = Paginator(products,16)
    page_number = request.GET.get("page")

    try:
        page_obj = pag.page(page_number)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)

    context["pag"] = page_obj

    context["keyword"] = keyword
    context["min_value"] = min_value
    context["max_value"] = max_value
    context["sort"] = sort

    context["min_price_of_all_products"] = min_price_of_all_products
    context["max_price_of_all_products"] = max_price_of_all_products
    context["supplier"] = supplier 
    context["current_category"] = categ
    context["category"] = search_category
    print(search_category)
    return render(request, 'sanjog/sellerpage.html',context)

def blank(request):
    return render(request, "sanjog/blank.html")
