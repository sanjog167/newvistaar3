from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Supplier,Company
from products.models import Products,Category
from products.views import search_algorithm, search_manager
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count,Min,Max, Q
from django.http import JsonResponse
from django.template.loader import render_to_string



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

   
    
#def new_supplier_detail(request, slug):
#    search_dictionary = {}
#    search_dictionary["keyword"] = request.GET.get('keyword')
#    search_dictionary["sort"] = request.GET.get("sort")
#    search_dictionary["min_value"] = request.GET.get("min_value")
#    search_dictionary["max_value"] = request.GET.get("max_value")
#
#    search_dictionary["subcategorys"] = request.GET.getlist('sub_categ')
#    search_dictionary["selected_brands"] = request.GET.getlist("brand")
#    
#    search_dictionary["seller_slug"] = slug 
#    search_dictionary["search_type"] = "seller"
#    products = search_manager(search_dictionary)
#    context = {} 
#
#    context['products'] = products
#
#    search_subcategory = []
#    brands = []
#    for p in products:
#        if not p.sub_category in search_subcategory:
#            search_subcategory.append(p.sub_category)
#        if p.brand != None and not p.brand in brands:
#            brands.append(p.brand)
#
#
#    pag = Paginator(products,16)
#    page_number = request.GET.get("page")
#
#    try:
#        page_obj = pag.page(page_number)
#    except PageNotAnInteger:
#        page_obj = pag.page(1)
#    except EmptyPage:
#        page_obj = pag.page(pag.num_pages)
#
#    context["products_count"] = products.count()
#
#    context["pag"] = page_obj
#
#    context["subcategory"] = search_subcategory
#    context["brands"] = brands
#    context["keyword"] = search_dictionary["keyword"]
#    # from search_dictionary['keyword'] find me a list of subcategories
#    all_filters = Products.objects.select_related("supplier").filter(supplier__slug=slug)
#    all_subcategories = []
#    all_brands = []
#    if search_dictionary["keyword"] != None:
#        max_price_of_all_products = Products.objects.filter(Q(product_name__icontains=search_dictionary["keyword"])).aggregate(max_price=Max('price'))['max_price'] 
#        min_price_of_all_products = Products.objects.filter(Q(product_name__icontains=search_dictionary["keyword"])).filter(price__gt=0).aggregate(min_price=Min('price'))['min_price'] 
#    else:
#        max_price_of_all_products = Products.objects.filter(supplier__slug=slug).aggregate(max_price=Max('price'))['max_price'] 
#        min_price_of_all_products = Products.objects.filter(supplier__slug=slug).filter(price__gt=0).aggregate(min_price=Min('price'))['min_price']
#    context["min_price_of_all_products"] = min_price_of_all_products
#    context["max_price_of_all_products"] = max_price_of_all_products
#
#    for subs in all_filters:
#        if subs.sub_category not in all_subcategories:
#            all_subcategories.append(subs.sub_category)
#        if subs.brand not in all_brands:
#            all_brands.append(subs.brand)
#    context["all_subcategories"] = all_subcategories
#    context["all_brands"] = all_brands
#    context["selected_subcats"] = search_dictionary["subcategorys"]
#    context["selected_brands"] = search_dictionary["selected_brands"]
#    
#    pagination_string_next = ""
#    pagination_string_prev = ""
#    if context["pag"].has_next(): 
#        pagination_string_next = ""
#        pagination_string_next += "?page=" + str(context["pag"].next_page_number())
#        if search_dictionary["keyword"] != None:
#            pagination_string_next += "&keyword=" + search_dictionary["keyword"]
#        if search_dictionary["subcategorys"] != None:
#            for subcat in search_dictionary["subcategorys"]:
#                pagination_string_next += "&sub_categ=" + subcat
#        if search_dictionary["selected_brands"] != None:
#            for brand in search_dictionary["selected_brands"]:
#                pagination_string_next += "&brand=" + brand
#        if search_dictionary["min_value"] != None:
#            pagination_string_next += "&min_value=" + search_dictionary["min_value"]
#        if search_dictionary["max_value"] != None:
#            pagination_string_next += "&max_value=" + search_dictionary["max_value"]
#        if search_dictionary["sort"] != None:
#            pagination_string_next += "&sort=" + search_dictionary["sort"]
#    
#    if context["pag"].has_previous(): 
#        pagination_string_prev = ""
#        pagination_string_prev += "?page=" + str(context["pag"].previous_page_number())
#        if search_dictionary["keyword"] != None:
#            pagination_string_prev += "&keyword=" + search_dictionary["keyword"]
#        if search_dictionary["subcategorys"] != None:
#            for subcat in search_dictionary["subcategorys"]:
#                pagination_string_prev += "&sub_categ=" + subcat
#        if search_dictionary["selected_brands"] != None:
#            for brand in search_dictionary["selected_brands"]:
#                pagination_string_prev += "&brand=" + brand
#        if search_dictionary["min_value"] != None:
#            pagination_string_prev += "&min_value=" + search_dictionary["min_value"]
#        if search_dictionary["max_value"] != None:
#            pagination_string_prev += "&max_value=" + search_dictionary["max_value"]
#        if search_dictionary["sort"] != None:
#            pagination_string_prev += "&sort=" + search_dictionary["sort"]
#   
#    context["pagination_string_next"] = pagination_string_next
#    context["pagination_string_prev"] = pagination_string_prev
#    context["supplier"] = Supplier.objects.get(slug=slug)
#    return render(request, "sanjog/sellerpage.html", context) 
    


def new_supplier_detail_ajax(request, slug):
    search_dictionary = {}
    search_dictionary["keyword"] = request.GET.get('keyword')
    search_dictionary["sort"] = request.GET.get("sort")
    search_dictionary["min_value"] = request.GET.get("min_value")
    search_dictionary["max_value"] = request.GET.get("max_value")

    search_dictionary["subcategorys"] = request.GET.getlist('sub_categ')
    search_dictionary["selected_brands"] = request.GET.getlist("brand")
    
    search_dictionary["seller_slug"] = slug 
    search_dictionary["search_type"] = "seller"
    print(search_dictionary)
    products = search_manager(search_dictionary)
    context = {} 

    context['products'] = products

    search_subcategory = []
    for p in products:
        if not p.sub_category in search_subcategory:
            search_subcategory.append(p.sub_category)


    pag = Paginator(products,16)
    page_number = request.GET.get("page")

    try:
        page_obj = pag.page(page_number)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)

    context["products_count"] = products.count()

    context["pag"] = page_obj

    context["subcategory"] = search_subcategory
    context["keyword"] = search_dictionary["keyword"]
    # from search_dictionary['keyword'] find me a list of subcategories
    #all_filters = Products.objects.select_related("supplier").filter(supplier__slug=slug)
    all_subcategories = []
    all_brands = []
    if search_dictionary["keyword"] != None:
        max_price_of_all_products = Products.objects.filter(Q(product_name__icontains=search_dictionary["keyword"])).aggregate(max_price=Max('price'))['max_price'] 
        min_price_of_all_products = Products.objects.filter(Q(product_name__icontains=search_dictionary["keyword"])).filter(price__gt=0).aggregate(min_price=Min('price'))['min_price'] 
    else:
        max_price_of_all_products = Products.objects.filter(supplier__slug=slug).aggregate(max_price=Max('price'))['max_price'] 
        min_price_of_all_products = Products.objects.filter(supplier__slug=slug).filter(price__gt=0).aggregate(min_price=Min('price'))['min_price']
    context["min_price_of_all_products"] = min_price_of_all_products
    context["max_price_of_all_products"] = max_price_of_all_products

    for subs in products:
        if subs.sub_category not in all_subcategories:
            all_subcategories.append(subs.sub_category)
        if subs.brand not in all_brands:
            all_brands.append(subs.brand)
    for b in all_brands:
        if b == "Not Mentioned":
            all_brands.remove(b)
            all_brands.append(b)
    context["all_subcategories"] = all_subcategories
    context["all_brands"] = all_brands
    context["selected_subcats"] = search_dictionary["subcategorys"]
    context["selected_brands"] = search_dictionary["selected_brands"]
    
    pagination_string_next = ""
    pagination_string_prev = ""
    if context["pag"].has_next(): 
        pagination_string_next = ""
        pagination_string_next += "?page=" + str(context["pag"].next_page_number())
        if search_dictionary["keyword"] != None:
            pagination_string_next += "&keyword=" + search_dictionary["keyword"]
        if search_dictionary["subcategorys"] != None:
            for subcat in search_dictionary["subcategorys"]:
                pagination_string_next += "&sub_categ=" + subcat
        if search_dictionary["selected_brands"] != None:
            for brand in search_dictionary["selected_brands"]:
                pagination_string_next += "&brand=" + brand
        if search_dictionary["min_value"] != None:
            pagination_string_next += "&min_value=" + search_dictionary["min_value"]
        if search_dictionary["max_value"] != None:
            pagination_string_next += "&max_value=" + search_dictionary["max_value"]
        if search_dictionary["sort"] != None:
            pagination_string_next += "&sort=" + search_dictionary["sort"]
    
    if context["pag"].has_previous(): 
        pagination_string_prev = ""
        pagination_string_prev += "?page=" + str(context["pag"].previous_page_number())
        if search_dictionary["keyword"] != None:
            pagination_string_prev += "&keyword=" + search_dictionary["keyword"]
        if search_dictionary["subcategorys"] != None:
            for subcat in search_dictionary["subcategorys"]:
                pagination_string_prev += "&sub_categ=" + subcat
        if search_dictionary["selected_brands"] != None:
            for brand in search_dictionary["selected_brands"]:
                pagination_string_prev += "&brand=" + brand
        if search_dictionary["min_value"] != None:
            pagination_string_prev += "&min_value=" + search_dictionary["min_value"]
        if search_dictionary["max_value"] != None:
            pagination_string_prev += "&max_value=" + search_dictionary["max_value"]
        if search_dictionary["sort"] != None:
            pagination_string_prev += "&sort=" + search_dictionary["sort"]
   
    context["pagination_string_next"] = pagination_string_next
    context["pagination_string_prev"] = pagination_string_prev
    context["supplier"] = Supplier.objects.get(slug=slug)
    context["featured_products"] = Products.objects.filter(supplier__slug=slug).filter(seller_top_product=True)[:5]
    #context["top_products"] = Products.objects.filter(supplier__slug=slug).filter(featured=True)[:5]
    if not request.is_ajax():
        return render(request, "sanjog/sellerpage_ajax.html", context) 
    else:
        content = ''
        for card in page_obj:
            content += render_to_string('sanjog/product_card.html',
                                        {'p': card},
                                        request=request)
        return JsonResponse({
            "content": content,
            "end_pagination": True if int(page_number) >= pag.num_pages else False,
        })
    
