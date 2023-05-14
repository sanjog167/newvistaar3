import re
from urllib import request
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from .models import Products,Category,Subcategory
from suppliers.models import Supplier
from account.models import Primary_leads, Message_box, Lead_messages
# from account.views import qr_update
from .forms import ProductEditForm, SubmitProductForm
from django.utils.text import slugify
from django.http import JsonResponse
import datetime
from django.db.models import Q, F
from account.views import send_lead_email, send_contact_view_email
import operator
from django.http import HttpResponseRedirect
from django.db.models import Count,Min,Max

from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.template.loader import render_to_string

from django.db.models import Case, IntegerField, Value, When
from django.core import serializers
from django.http import JsonResponse
import urllib.parse
from django.utils.safestring import mark_safe
def filter_values(request):
    """takes request and returns a dictionary of filtered values

    Args:
        request (request): request object
        
    Returns: dictionary of filtered values
    
    """
    parameters = {}
    parameters['category'] = request.GET.get('category')
    parameters['min_value'] = request.GET.get('min_value')
    parameters['max_value'] = request.GET.get('max_value')
    parameters['sort_by'] = request.GET.get('sort')
    parameters['keyword'] = request.GET.get('keyword')
    
    for key, value in parameters.items():
        if value == 'None':
            parameters[key] = None
    
    return parameters

def search_algorithm(category, sub_categ, keyword, min_value, max_value, sort_by, seller, _type):
    """takes arguments to apply queryset filter to

    Args:
        category (str): specific category selected by user
        keyword (str): keyword to search for in product
        min_value (str): minimum value to filter upwards
        max_value (str): maximum value to filter to
        sort_by (str): type of sort (eg latest, low to high, high to low)
        seller (str): specific seller selected by user
        _type (str): type of search (search, category, subcategory, sellerpage)

    Returns:
        queryset : matching queryset return
    """
    
    if _type == "search":
        keyword_filtered = None
        # if category is given
        if category != None:
            keyword_filtered = Products.objects.select_related().filter(category__title=category)
        elif keyword != None and keyword != "None" and keyword != "": # else atleast keyword is sure to be given
            keyword_filtered = Products.objects.select_related().filter(Q(product_name__icontains=keyword)|Q(description__icontains=keyword)|Q(keywords__icontains=keyword))
        else:
            keyword_filtered = Products.objects.select_related()
        # filter by keyword if present
        if keyword != None and category != None and keyword != "None" and keyword != "":
            keyword_filtered = keyword_filtered.filter(Q(product_name__icontains=keyword)|Q(description__icontains=keyword)|Q(keywords__icontains=keyword))
        # filter by subcategory if present
        if sub_categ != None and sub_categ != "None" and sub_categ != "":
            keyword_filtered = keyword_filtered.filter(sub_category=sub_categ)
        # filter by min and max value if present
        if min_value != None:
            keyword_filtered = keyword_filtered.filter(price__gte=min_value)
        if max_value != None:
            keyword_filtered = keyword_filtered.filter(price__lte=max_value)
        # filter by seller if present
        if seller != None and seller != "None" and seller != "":
            keyword_filtered = keyword_filtered.filter(supplier=seller)
        # sort by latest, low to high, high to low
        if sort_by == "LST":
            keyword_filtered = keyword_filtered.order_by("-id")
        elif sort_by == "LTH":
            keyword_filtered = keyword_filtered.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
        elif sort_by == "HTL":
            keyword_filtered = keyword_filtered.order_by("-price")
        return keyword_filtered
    
    elif _type == "category":
        category_filtered = Products.objects.select_related().filter(category__title=category)
        if keyword != None:
            category_filtered = category_filtered.filter(Q(product_name__icontains=keyword)|Q(description__icontains=keyword)|Q(keywords__icontains=keyword))
        if min_value != None:
            category_filtered = category_filtered.filter(price__gte=min_value)
        if max_value != None:
            category_filtered = category_filtered.filter(price__lte=max_value)
        # sort by latest, low to high, high to low
        if sort_by == "LST":
            category_filtered = category_filtered.order_by("-id")
        elif sort_by == "LTH":
            category_filtered = category_filtered.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
        elif sort_by == "HTL":
            category_filtered = category_filtered.order_by("-price")
        return category_filtered
        
    
    elif _type == "subcategory":
        subcategory_filtered = Products.objects.select_related().filter(sub_category=category)
        if keyword != None:
            subcategory_filtered = subcategory_filtered.filter(Q(product_name__icontains=keyword)|Q(description__icontains=keyword)|Q(keywords__icontains=keyword))
        if min_value != None:
            subcategory_filtered = subcategory_filtered.filter(price__gte=min_value)
        if max_value != None:
            subcategory_filtered = subcategory_filtered.filter(price__lte=max_value)
        # sort by latest, low to high, high to low
        if sort_by == "LST":
            subcategory_filtered = subcategory_filtered.order_by("-id")
        elif sort_by == "LTH":
            subcategory_filtered = subcategory_filtered.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
        elif sort_by == "HTL":
            subcategory_filtered = subcategory_filtered.order_by("-price")
        return subcategory_filtered

    
    elif _type == "sellerpage":
       products_from_given_seller = Products.objects.select_related().filter(supplier__slug=seller).order_by("-clicks")
       # filter by keyword if present
       if keyword != None:
           products_from_given_seller = products_from_given_seller.filter(Q(product_name__icontains=keyword)|Q(description__icontains=keyword)|Q(keywords__icontains=keyword))
       # filter by subcategory if present
       if category != None:
           products_from_given_seller = products_from_given_seller.filter(category__slug=category)
       # filter by min and max value if present
       if min_value != None:
           products_from_given_seller = products_from_given_seller.filter(price__gte=min_value)
       if max_value != None:
           products_from_given_seller = products_from_given_seller.filter(price__lte=max_value)
       # sort by latest, low to high, high to low
       if sort_by == "LST" or sort_by == None or sort_by == "":
           products_from_given_seller = products_from_given_seller.order_by("-id")
       elif sort_by == "LTH":
           products_from_given_seller = products_from_given_seller.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
       elif sort_by == "HTL":
           products_from_given_seller = products_from_given_seller.order_by("-price")
       elif sort_by == "popular":
           products_from_given_seller = products_from_given_seller.order_by("-clicks")
       return products_from_given_seller
# Create your views here.

class HomeView(TemplateView):
    template_name = "sanjog/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fcategories = Category.objects.filter(featured=True).order_by("id")
        all_products = Products.objects.filter(featured=True).order_by("-id")
        categories = Category.objects.all().order_by("id")

        trending = Products.objects.all().order_by("-clicks")[:10]
        subcat = Subcategory.objects.all().order_by("-id")
        # c1 = Category.objects.get(slug='kitchen-utensils')
        # c2 = Category.objects.get(slug='handicraft')
        # c3 = Category.objects.get(slug='cosmetics')
        c1 = Category.objects.get(slug='building-construction')
        c2 = Category.objects.get(slug='industrial-machinery-suplies')
        c3 = Category.objects.get(slug='consumer-electronics')
        cat1 = Products.objects.filter(featured=True).order_by("-clicks").filter(category=c1)[:10]
        cat2 = Products.objects.filter(featured=True).order_by("-clicks").filter(category=c2)[:10]
        cat3 = Products.objects.filter(featured=True).order_by("-clicks").filter(category=c3)[:10]
        context['fcategories'] = fcategories
        context['products'] = all_products
        context['categories'] = categories
        context['trending'] = trending
        context['cat1'] = cat1
        context['cat2'] = cat2
        context['cat3'] = cat3
        context['subcat'] = subcat

        return context


def product_detail(request,id,slug):
    product = get_object_or_404(Products,id=id,slug=slug,available=True)

    if request.method == 'POST':

        new_lead = Primary_leads(seller = product.supplier, buyer = request.user, product = product)
        new_lead.save()

        #related

        mbox_title = str(product.supplier) + " - " + request.user.first_name + " - " + str(product)

        new_mbox = Message_box(lead = new_lead, title = mbox_title, initiated = datetime.datetime.now(), seller=product.supplier.user, buyer= request.user)
        new_mbox.save()

        first_message = Lead_messages(m_box = new_mbox, content = new_lead.get_message(), sender = request.user, reciever = product.supplier.user, time = datetime.datetime.now() )
        first_message.save()

        return render(request,'dashboard/lead_created.html',{'success':'Success'})

    else:

        product.clicks += 1
        product.save()
        pcategory = product.category
        cat = Products.objects.filter(category=pcategory)

        supplier = product.supplier
        one=0
        two=0
        three=0
        four=0
        five=0
        
        # for r in supplier.rating:
        #     match r:
        #         case '1': one =+ 1
        #         case '2': two =+ 1
        #         case '3': three =+ 1
        #         case '4': four =+ 1
        #         case '5' : five =+ 1

        total_rate = one + two + three + four + five
        print(one,two,three,four,five)
        url_encoded_string = urllib.parse.quote(f"Hello! I am {request.user} from Vistaartrade.com. I want to enquire about your {product}.") 
        table_regex = re.compile(r'<figure\b[^>]*>.*?</figure>', re.IGNORECASE | re.DOTALL)

# Remove the table tag and its contents from the HTML string
        cleaned_html_string = table_regex.sub('', product.description)
        cleaned_html_string = mark_safe(cleaned_html_string)
        return render(request,'sanjog/product-detail.html',{'product':product,'cat':cat,'one':one,'two':two,'three':three,'four':four,'five':five,'total':total_rate, 'url_encoded_string': url_encoded_string, 'short_desc': cleaned_html_string})



def all_category_detail(request):
    return category_detail(request, None, None)


def category_detail(request,id,slug):
    context = {}

    category = None
    if id != None:
        category = get_object_or_404(Category,id=id,slug=slug)
    sub_categ = None
    if request.GET.get("sub_categ") != None and request.GET.get("sub_categ") != "None" and request.GET.get("sub_categ") != "":
        sub_categ = get_object_or_404(Subcategory,slug=request.GET.get("sub_categ"))
    keyword = request.GET.get("keyword")
    sort = request.GET.get("sort")
    min_value = request.GET.get("min_value")
    max_value = request.GET.get("max_value")
    selected_brands = request.GET.getlist("brands")
    context["selected_brands"] = selected_brands
    supplier = request.GET.get("supplier")
    if supplier != None:
        supplier_obj = get_object_or_404(Supplier, slug=supplier)
    else:
        supplier_obj = None

    products = search_algorithm(category, sub_categ, keyword, min_value, max_value, sort, seller=supplier_obj, _type="search")

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

    search_seller = []
    search_subcategory = []
    brands = []
    for p in products:
        if not p.supplier in search_seller:
            search_seller.append(p.supplier)    
        if not p.sub_category in search_subcategory:
            search_subcategory.append(p.sub_category)
        if p.price < min_price_of_all_products:
            min_price_of_all_products = p.price
        if p.price > max_price_of_all_products:
            max_price_of_all_products = p.price
        if p.brand != None and not p.brand in brands:
            brands.append(p.brand)

    # Now filter by category
    if category != None:
        products = products.filter(category=category)

    # Now filter by brands
    if len(selected_brands) != 0:
        products = products.filter(brand__in=selected_brands)

    # Pagination

    pag = Paginator(products,16)
    page_number = request.GET.get("page")

    try:
        page_obj = pag.page(page_number)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)

    context["products_count"] = products.count()

    context["slug"] = slug
    context["current_category"] = category
    context["current_subcategory"] = sub_categ
    context["current_supplier"] = supplier_obj
    context["pag"] = page_obj
    context["sub_category"] = Subcategory.objects.filter(category=category)

    context["sub_categ"] = request.GET.get("sub_categ")
    context["keyword"] = keyword
    context["min_value"] = min_value
    context["max_value"] = max_value
    context["sort"] = sort

    context["min_price_of_all_products"] = min_price_of_all_products
    context["max_price_of_all_products"] = max_price_of_all_products
    context["supplier"] = search_seller
    context["subcategory"] = search_subcategory
    context["brands"] = brands
    return render(request, 'sanjog/category_page.html',context)
    
def subcategory_detail(request,id,slug):
    context = {}
    subcategory = get_object_or_404(Subcategory,id=id,slug=slug)
    parameters = filter_values(request)
    parameters['category'] = subcategory
    products = search_algorithm(**parameters, seller=None, _type="subcategory")
    print(products)
    pag = Paginator(products,16)
    page_number = request.GET.get("page")
    try:
        page_obj = pag.page(page_number)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)
    context["current_category"] = subcategory
    context["products"] = products
    context["pag"] = page_obj
    context["keyword"] = parameters["keyword"]
    context["min_value"] = parameters["min_value"]
    context["max_value"] = parameters["max_value"]
    context["sort_by"] = parameters["sort_by"]
    context["category_breadcrumb"] = subcategory.category
    min_price_of_all_products = 0
    max_price_of_all_products = 0
    try:
        max_price_of_all_products = products[0].price
    except:
        pass
    search_seller = []
    for p in products:
        if not p.supplier in search_seller:
            search_seller.append(p.supplier)    

        if p.price < min_price_of_all_products:
            min_price_of_all_products = p.price
        if p.price > max_price_of_all_products:
            max_price_of_all_products = p.price
    context["min_price_of_all_products"] = min_price_of_all_products
    context["max_price_of_all_products"] = max_price_of_all_products
    context["supplier"] = search_seller
    return render(request, 'sanjog/subcategory_page.html',context)

# def submit_product(request):
#     current_user = request.user
#     categories = Category.objects.all().order_by("id")

#     if request.method == 'POST':
#         submit_product_form = SubmitProductForm(request.POST,request.FILES or None)

#         cat_id = Category.objects.get(id=request.POST['category'])
#         subcat_id = Subcategory.objects.get(id=20)

#         new_product = Products.objects.create(product_name=request.POST['product-name'],
#                                                 description=request.POST['description'],
#                                                 category=cat_id,
#                                                 price=0, max_price=0,
#                                                 supplier = current_user.supplier,
#                                                 minimum_order_quantity="1 pcs",
#                                                 sub_category = subcat_id
#                                                 )
        
#         new_product.slug = slugify(new_product.product_name)
#         new_product.save()
        
#         messages.success(request, 'Your product has successfully been added!')
    
#         return redirect('products:submit_product')

#     else:
#         submit_product_form = SubmitProductForm()
        
#     return render(request, 'products/product_add.html',{'submit_product_form':submit_product_form,'categories':categories})

def submit_product(request):
    current_user = request.user

    if request.method == 'POST':
        submit_product_form = SubmitProductForm(request.POST,request.FILES or None)

        print("HEREEEEE")
        print(request.POST)

        if request.POST['product-name'] == '':
            messages.success(request,'Please Enter a name')
            return redirect('products:submit_product')        

        if request.POST['category'] != '0':
            cat_id = Category.objects.get(id=request.POST['category'])
        else:
            messages.success(request,'Select a category!')
            return redirect('products:submit_product')
        
        if request.POST['sub-category'] != '0':    
            subcat_id = Subcategory.objects.get(id=request.POST['sub-category'])
        else:
            messages.success(request,'Select a sub-category!')
            return redirect('products:submit_product')

        new_slug = slugify(request.POST['product-name'])

        new_product = Products.objects.create(product_name=request.POST['product-name'],
                                                 slug = new_slug,
                                                 description=request.POST['description'],
                                                 category=cat_id,
                                                 price=request.POST['min-price'],
                                                 max_price=request.POST['max-price'],
                                                 supplier = current_user.supplier,
                                                 minimum_order_quantity=request.POST['min-qty'],
                                                 sub_category = subcat_id,
                                                 brand = request.POST['brand'],
                                                 )
        
        if 'image1' in request.FILES:

            new_product.image = request.FILES['image1']


        if 'image2' in request.FILES:

            new_product.image2 = request.FILES['image2']


        if 'image3' in request.FILES:

            new_product.image3 = request.FILES['image3']


        if 'image4' in request.FILES:

            new_product.image4 = request.FILES['image4']


        new_product.save()

        messages.success(request, 'Your product has successfully been added!')
        if 'back_to_manage_products' in request.POST:
            return redirect('manage_products') 
        return redirect('products:submit_product')

    else:
        submit_product_form = SubmitProductForm()

        categories = Category.objects.all()
        sub_categories = Subcategory.objects.all()
        
    return render(request, 'sanjog/add-product.html',{'submit_product_form':submit_product_form,'cat':categories,'subcat':sub_categories})

def edit_product(request,id):
    context = {}
    if request.method == 'POST':

        submit_product_form = SubmitProductForm(request.POST,request.FILES or None)

        if request.POST['category'] != '0':
            cat_id = Category.objects.get(id=request.POST['category'])
        else:
            messages.success(request,'Select a category!')
            return redirect('products:submit_product')
        
        if request.POST['sub-category'] != '0':    
            subcat_id = Subcategory.objects.get(id=request.POST['sub-category'])
        else:
            messages.success(request,'Select a sub-category!')
            return redirect('products:submit_product')
        
        Products.objects.filter(id=id).update(product_name=request.POST['product-name'],
                                                 description=request.POST['description'],
                                                 category=cat_id,
                                                 price=request.POST['min-price'],
                                                 max_price=request.POST['max-price'],
                                                 minimum_order_quantity=request.POST['min-qty'],
                                                 brand=request.POST['brand'],
                                                 sub_category = subcat_id)

        new = Products.objects.get(id=id)

        if 'image1' in request.FILES:
            new.image = request.FILES['image1']

        if 'image2' in request.FILES:
            new.image2 = request.FILES['image2']

        if 'image3' in request.FILES:
            new.image3 = request.FILES['image3']

        if 'image4' in request.FILES:
            new.image4 = request.FILES['image4']


        new.save()

        messages.success(request, 'Your product has successfully been edited!')
    
        return redirect('manage_products')
    else:
        
        product = Products.objects.get(id=id)
        submit_product_form = SubmitProductForm(initial={'product_name':'hi'})
        categories = Category.objects.all()
        sub_categories = Subcategory.objects.all()
        
        context['prepopulated_category_name'] = product.category
        context['prepopulated_sub_category_name'] = product.sub_category
        context['prepopulated_category_id'] = product.category.id
        context['prepopulated_sub_category_id'] = product.sub_category.id
        context['prepopulated_brand'] = product.brand
        context['submit_product_form'] = submit_product_form
        context['product'] = product
        context['cat'] = categories
        context['subcat'] = sub_categories
        return render(request, 'products/edit.html', context)

 
@login_required
def get_best_price(request, id):
    if request.method == 'POST':
        current_user = request.user.username
        buyer = User.objects.get(username=current_user)
        product = Products.objects.get(id=id)
        supplier = product.supplier

        quantity_required = request.POST['quantity']
        request_description = request.POST['description']

        primary_leads = Primary_leads(seller=supplier, buyer=buyer, product=product,
                                    quantity_required=quantity_required,
                                    request_description=request_description)
        primary_leads.save()

        
        send_lead_email(current_user,supplier,product,request, quantity_required)

        #Similar product leads to pro and premium sellers

        keywords = product.keywords
        #for key in keywords:

        messages.success(request,"Your request has been successfully sent to:")
        return redirect(product)
    else:
        return render(request, 'product/detail.html')


# @login_required
# def edit_product(request, id):
#     product = Products.objects.get(pk=id)

#     if request.method == 'POST':
#         product_form = ProductEditForm(instance=product,
#                                     data=request.POST,
#                                     files=request.FILES)
#         if product_form.is_valid():
#             product_form.save()
#     else:
#         product_form = ProductEditForm(instance=product)
#     return render(request,
#                   'products/edit.html',
#                   {'product_form': product_form})


#class SearchView(TemplateView):
#    template_name="sanjog/categorypage.html"
#    
#    def get_context_data(self,**kwargs):
#        context = super().get_context_data(**kwargs)
#        print(self.request.GET)
#        kw = self.request.GET.get("keyword")
#        category = self.request.GET.get("category")
#        latest = self.request.GET.get("latest")
#        lth = self.request.GET.get("lth")
#        htl = self.request.GET.get("htl")
#        #print("HEREEEEEEEE")
#        #print(kw,category)
#        #print("latest", latest, lth, htl)
#        #### query for lowest to highest price
#        #from django.db.models import Case, IntegerField, Value, When
#        #Products.objects.select_related().filter(Q(product_name__icontains=kw)|Q(description__icontains=kw)|Q(keywords__icontains=kw)).annotate(zero_price=Case(When(price=0, then=Value(999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
#        #### query for highest to lowest price
#        #Products.objects.select_related().filter(Q(product_name__icontains=kw)|Q(description__icontains=kw)|Q(keywords__icontains=kw)).order_by("-price")
#        if str(category) == "None":
#            results = Products.objects.select_related().filter(Q(product_name__icontains=kw)|Q(description__icontains=kw)|Q(keywords__icontains=kw))
#        else:
#            results = Products.objects.select_related().filter(Q(product_name__icontains=kw)|Q(description__icontains=kw)|Q(supplier__company_name__icontains=kw)|Q(keywords__icontains=kw)).filter(category__title=category)
#
#        search_category = []
#        search_seller = []
#    
#        for p in results:
#            if not p.category in search_category:
#                search_category.append(p.category)
#
#            if not p.supplier in search_seller:
#                search_seller.append(p.supplier)    
#                
#                
#        context["keyword"] = kw
#        context["category"] = search_category
#        context["supplier"] = search_seller
#        context["results"] = results
#        context["scat"] = category
#        
#
#        pag = Paginator(results,16)
#        page_number = self.request.GET.get("page")
#
#        try:
#            page_obj = pag.page(page_number)
#        except PageNotAnInteger:
#            page_obj = pag.page(1)
#        except EmptyPage:
#            page_obj = pag.page(pag.num_pages)
#
#
#        context["pag"] = page_obj
#
#        return context


#class SearchView(TemplateView):
#    template_name = "sanjog/search_page.html"
#    def get_context_data(self,**kwargs):
#        context = super().get_context_data(**kwargs)
#        context['first_load'] = 1
#        kw = self.request.GET.get("keyword")
#        sort = self.request.GET.get("sort")
#        min_value = self.request.GET.get("min_value")
#        max_value = self.request.GET.get("max_value")
#        if kw == None:
#            kw = ""
#            context['first_load'] = 0
#            return context
#        category = self.request.GET.get("category")
#        if category == "None":
#            category = None
#        if min_value == "None":
#            min_value = None
#        if max_value == "None":
#            max_value = None
#        results = search_algorithm(category, kw, min_value, max_value, sort, seller=None, _type="search") 
#        context['results'] = results
#        search_category = []
#        search_seller = []
#
#        min_price_of_all_products = 0
#        max_price_of_all_products = 0
#        try:
#            max_price_of_all_products = results[0].price
#        except:
#            pass
#
#        for p in results:
#            if p.price < min_price_of_all_products:
#                min_price_of_all_products = p.price
#            if p.price > max_price_of_all_products:
#                max_price_of_all_products = p.price
#
#        # filter by min and max value if present on all products containing keyword
#        if min_value != None:
#            results = results.filter(price__gte=min_value)
#        else:
#            min_value = 0
#        if max_value != None:
#            results = results.filter(price__lte=max_value)
#        else:
#            max_value = max_price_of_all_products
#
#        context['results'] = results
#        search_category = []
#        search_seller = []
#
#        for p in results:
#            if not p.category in search_category:
#                search_category.append(p.category)
#
#            if not p.supplier in search_seller:
#                search_seller.append(p.supplier)    
#
#        context["keyword"] = kw
#        context["current_category"] = category
#        context["category"] = search_category
#        context["supplier"] = search_seller
#        context["scat"] = category
#
#        context["min_value"] = min_value
#        context["max_value"] = max_value
#        context["min_price_of_all_products"] = min_price_of_all_products
#        context["max_price_of_all_products"] = max_price_of_all_products
#
#        pag = Paginator(results,16)
#        page_number = self.request.GET.get("page")
#
#        try:
#            page_obj = pag.page(page_number)
#        except PageNotAnInteger:
#            page_obj = pag.page(1)
#        except EmptyPage:
#            page_obj = pag.page(pag.num_pages)
#
#
#        context["pag"] = page_obj
#        context['keyword'] = kw
#        context['sort'] = sort
#        return context


def post_requirements_livesearch(request):
    if request.is_ajax():
        res = None
        prods = request.GET.get('prod')
        results = Products.objects.select_related('sub_category').filter(Q(product_name__icontains=prods)|Q(description__icontains=prods)|Q(keywords__icontains=prods))
        subcategories = results.order_by().values_list('sub_category', flat=True).distinct()
        if len(results)>0 and len(prods)>0:
            rec_subcats = []
            for subcat in subcategories:
                s = Subcategory.objects.get(pk=subcat)
                item = {
                    'pk': s.pk,
                    'name': f"{prods} in {s}",
                }
                rec_subcats.append(item)
            rec_subcats = rec_subcats[:5]
        else:
            rec_subcats = "No products found ..."
        return JsonResponse({'subcats': rec_subcats})
    return JsonResponse({})


def livesearch(request):
    if request.is_ajax():
        res = None
        prods = request.GET.get('prod')
        results = Products.objects.select_related('sub_category').filter(Q(product_name__icontains=prods)|Q(keywords__icontains=prods))
        subcategories = results.order_by().values_list('sub_category', flat=True).distinct()
        if len(results)>0 and len(prods)>0:
            data = []
            for pos in results:
                item = {
                    'pk':pos.pk,
                    'name':pos.product_name,
                    'slug':pos.slug,
                }
                data.append(item)
            rec_subcats = []
            for subcat in subcategories:
                s = Subcategory.objects.get(pk=subcat)
                item = {
                    'name': f"{prods} in {s}",
                    'url': f"/products/category/{s.category.id}/{s.category.slug}/?subcat={s.slug}&keyword={prods}"
                }
                rec_subcats.append(item)
            res = data[:10]
            #rec_subcats = rec_subcats[:10]
        else:
            res = "No products found ..."
        return JsonResponse({'data':res, 'subcats': rec_subcats})
    return JsonResponse({})

def privacy_policy(request):
    
    success = 1
    
    return render(request, 'vistaar/privacy.html',{'success':success,})

def about_us(request):
    
    success = 1
    
    return render(request, 'sanjog/about.html',{'success':success,})

def error(request):
    
    success = 1
    
    return render(request, 'sanjog/error.html',{'success':success,})

def seller_become(request):
    
    success = 1
    
    return render(request, 'sanjog/seller.html',{'success':success,})

def email_verify(request):
    
    success = 1
    
    return render(request, 'sanjog/verifyemail.html',{'success':success,})

def emailverify(request):
    
    success = 1
    
    return render(request, 'sanjog/emailverify.html',{'success':success,})

def emailinquiry(request):
    
    success = 1
    
    return render(request, 'sanjog/emailinquiry.html',{'success':success,})

def emailopenrequest(request):
    
    success = 1
    
    return render(request, 'sanjog/emailopenrequest.html',{'success':success,})

def emailforgotpassword(request):
    
    success = 1
    
    return render(request, 'sanjog/emailforgotpassword.html',{'success':success,})

def seller_leads(request):
    
    success = 1
    
    return render(request, 'sanjog/leads.html',{'success':success,})

def email(request):
    
    success = 1
    
    return render(request, 'sanjog/email.html',{'success':success,})

def trending_products(request):
    success = 1
    trending = Products.objects.all().order_by("-clicks")[:24]
    context = {
        'success': success,
        'trending': trending,
    }
    return render(request, 'sanjog/trending_products.html', context)

    





def seller_page(request):
    
    success = 1
    
    return render(request, 'sanjog/sellerpage.html',{'success':success,})
    
def terms_conditions(request):
    
    success = 1
    
    return render(request, 'vistaar/terms.html',{'success':success,})

   
    

def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        dict_obj[key] += 1
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = value

def keyword_data(request):

    all_products = Products.objects.all()
    key_dict = {}

    for p in all_products:
        keys = p.keywords
        for x in keys:
            append_value(key_dict,x,1) 

    #sorted_d = dict(sorted(key_dict.items(), key=operator.itemgetter(1),reverse=True))
    return render(request,'admin/keyword_data.html',{'keywords':key_dict})


#filterproducts
def filter_data_sort(request):
    # cats = request.GET.getlist('category[]')
    # print(cats)#returns list of category id
    # minprice = request.GET['minPrice']
    # actprice = request.GET['actualPrice']
    sortval = request.GET['sortVal']
    keyval = request.GET['keyWord']

    print(sortval)
    if sortval == "lst":
        allproducts = Products.objects.filter(Q(product_name__icontains=keyval)|Q(description__icontains=keyval)|Q(supplier__company_name__icontains=keyval)|Q(keywords__icontains=keyval)).order_by('-id').distinct()
    elif sortval == "LTH":
        allproducts = Products.objects.filter(Q(product_name__icontains=keyval)|Q(description__icontains=keyval)|Q(supplier__company_name__icontains=keyval)|Q(keywords__icontains=keyval)).order_by('price').distinct()#order_by('-id') gives recent first,distinct helps to omit duplicate products
    else:
        allproducts = Products.objects.filter(Q(product_name__icontains=keyval)|Q(description__icontains=keyval)|Q(supplier__company_name__icontains=keyval)|Q(keywords__icontains=keyval)).order_by('-price').distinct()
    # allproducts = allproducts.filter(price__gte=minprice)
    # allproducts = allproducts.filter(price__lte=actprice)
    # catcount = allproducts.count()
    # if len(cats)>0:#in other words if category exist
        # allproducts = allproducts.filter(category__id__in=cats).distinct()
        # catcount = allproducts.count()
        # print(allproducts)

    pag = Paginator(allproducts,16)
    page_number = request.GET.get("page")

    try:
        page_obj = pag.page(page_number)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)
    
    t = render_to_string('ajax/filtercategorypage.html',# creates template to the string and returning product list page to t variable with the help of render_to_string
        {
            'pag':page_obj,
        })
    return JsonResponse({'data':t})

#filterproducts
def filter_data_price(request):
    # cats = request.GET.getlist('category[]')
    # print(cats)#returns list of category id
    minprice = request.GET['minPrice']
    maxprice = request.GET['maxPrice']
    allproducts = Products.objects.all().distinct()
    allproducts = allproducts.filter(price__gte=minprice)
    allproducts = allproducts.filter(price__lte=maxprice)
    # catcount = allproducts.count()
    # if len(cats)>0:#in other words if category exist
        # allproducts = allproducts.filter(category__id__in=cats).distinct()
        # catcount = allproducts.count()
        # print(allproducts)

    pag = Paginator(allproducts,16)
    page_number = request.GET.get("page")

    try:
        page_obj = pag.page(page_number)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)
    
    t = render_to_string('ajax/filtercategorypage.html',# creates template to the string and returning product list page to t variable with the help of render_to_string
        {
            'pag':page_obj,
        })
    return JsonResponse({'data':t})        

def filter_data(request):
    # cats = request.GET.getlist('category[]')
    # print(cats)#returns list of category id
    # minprice = request.GET['minPrice']
    # actprice = request.GET['actualPrice']
    sortval = request.GET['sortVal']
    print(sortval)
    if sortval == "lst":
        allproducts = Products.objects.all().order_by('-id').distinct()
    elif sortval == "LTH":
        allproducts = Products.objects.all().order_by('price').distinct()#order_by('-id') gives recent first,distinct helps to omit duplicate products
    else:
        allproducts = Products.objects.all().order_by('-price').distinct()
    # allproducts = allproducts.filter(price__gte=minprice)
    # allproducts = allproducts.filter(price__lte=actprice)
    # catcount = allproducts.count()
    # if len(cats)>0:#in other words if category exist
        # allproducts = allproducts.filter(category__id__in=cats).distinct()
        # catcount = allproducts.count()
        # print(allproducts)

    pag = Paginator(allproducts,16)
    page_number = request.GET.get("page")

    try:
        page_obj = pag.page(page_number)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)
    
    t = render_to_string('ajax/categorypage.html',# creates template to the string and returning product list page to t variable with the help of render_to_string
        {
            'pag':page_obj,
        })
    return JsonResponse({'data':t})

   
@login_required
def alert_supplier(request, id):
    if request.method == 'POST':
        current_user = request.user.username
        buyer = User.objects.get(username=current_user)
        product = Products.objects.get(id=id)
        supplier = product.supplier

        send_contact_view_email(current_user,supplier,product,request)


        messages.success(request,"Your request has been successfully sent to:")
        return redirect(product)
    else:
        return render(request, 'product/detail.html')
    

def get_subcategorys(request, id):
    subcats = Subcategory.objects.select_related('category').filter(category_id=id)
    data = serializers.serialize('json', subcats, fields=('title', 'category'))
    return JsonResponse({'data': data})

def test_get_category(request):
    categories = Category.objects.all()
    return render(request, 'sanjog/test_category.html',{'cat':categories})


def test(request):
    subcategorys = request.GET.getlist('sub_categ')
    sellers = request.GET.getlist('seller')
    keyword = request.GET.get('keyword')
    products = Products.objects.filter(sub_category__slug__in=subcategorys).filter(Q(product_name__icontains=keyword)|Q(description__icontains=keyword)|Q(supplier__company_name__icontains=keyword)|Q(keywords__icontains=keyword))
    print(products)
    return JsonResponse({'data': 'hello'})


def search_manager(search_dictionary):
    if search_dictionary["search_type"] == "normal":
        result = Products.objects.select_related("supplier").filter(Q(product_name__icontains=search_dictionary["keyword"])|Q(description__icontains=search_dictionary["keyword"])|Q(supplier__company_name__icontains=search_dictionary["keyword"])|Q(keywords__icontains=search_dictionary["keyword"]))
        if search_dictionary["subcategorys"] != []:
            result = result.filter(sub_category__slug__in=search_dictionary["subcategorys"])
        if search_dictionary["selected_brands"] != []:
            result = result.filter(brand__in=search_dictionary["selected_brands"])
        if search_dictionary["selected_business"] != []:
            for search_item in search_dictionary["selected_business"]:
                result = result.filter(supplier__secondary_business__icontains=search_item)
        if search_dictionary["sellers"] != []:
            result = result.filter(supplier__slug__in=search_dictionary["sellers"])
        if search_dictionary["min_value"] != None and search_dictionary["min_value"] != "":
            result = result.filter(price__gte=search_dictionary["min_value"])
        if search_dictionary["max_value"] != None and search_dictionary["max_value"] != "":
            result = result.filter(price__lte=search_dictionary["max_value"])
        if search_dictionary["sort"] == "LST":
            result = result.order_by("-id")
        elif search_dictionary["sort"] == "LTH":
            result = result.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
        elif search_dictionary["sort"] == "HTL":
            result = result.order_by("-price")
        return result
    
    if search_dictionary["search_type"] == "trending":
        result = Products.objects.all().order_by("-clicks")[:100]
        if search_dictionary["keyword"] == "" and search_dictionary["keyword"] == None and search_dictionary["keyword"] == "None":
            print("keyword", search_dictionary["keyword"])
            result = Products.objects.select_related("supplier").filter(Q(product_name__icontains=search_dictionary["keyword"])|Q(description__icontains=search_dictionary["keyword"])|Q(supplier__company_name__icontains=search_dictionary["keyword"])|Q(keywords__icontains=search_dictionary["keyword"])).order_by("-clicks")
        if search_dictionary["subcategorys"] != []:
            result = result.filter(sub_category__slug__in=search_dictionary["subcategorys"])
        if search_dictionary["selected_brands"] != []:
            result = result.filter(brand__in=search_dictionary["selected_brands"])
        if search_dictionary["sellers"] != []:
            result = result.filter(supplier__slug__in=search_dictionary["sellers"])
        if search_dictionary["min_value"] != None and search_dictionary["min_value"] != "":
            result = result.filter(price__gte=search_dictionary["min_value"])
        if search_dictionary["max_value"] != None and search_dictionary["max_value"] != "":
            result = result.filter(price__lte=search_dictionary["max_value"])
        if search_dictionary["sort"] == "LST":
            result = result.order_by("-id")
        elif search_dictionary["sort"] == "LTH":
            result = result.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
        elif search_dictionary["sort"] == "HTL":
            result = result.order_by("-price")
        return result
    

    if search_dictionary["search_type"] == "category":
        result = Products.objects.select_related("supplier").filter(category=search_dictionary["category_id"])
        if search_dictionary["subcategorys"] != []:
            result = result.filter(sub_category__slug__in=search_dictionary["subcategorys"])
        if search_dictionary["selected_brands"] != []:
            result = result.filter(brand__in=search_dictionary["selected_brands"])
        if search_dictionary["sellers"] != []:
            result = result.filter(supplier__slug__in=search_dictionary["sellers"])
        if search_dictionary["min_value"] != None:
            result = result.filter(price__gte=search_dictionary["min_value"])
        if search_dictionary["max_value"] != None:
            result = result.filter(price__lte=search_dictionary["max_value"])
        if search_dictionary["sort"] == "LST":
            result = result.order_by("-id")
        elif search_dictionary["sort"] == "LTH":
            result = result.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
        elif search_dictionary["sort"] == "HTL":
            result = result.order_by("-price")
        return result
    
    if search_dictionary["search_type"] == "subcategory":
        result = Products.objects.select_related("supplier").filter(sub_category=search_dictionary["subcategory_id"])
        if search_dictionary["selected_brands"] != []:
            result = result.filter(brand__in=search_dictionary["selected_brands"])
        if search_dictionary["sellers"] != []:
            result = result.filter(supplier__slug__in=search_dictionary["sellers"])
        if search_dictionary["min_value"] != None:
            result = result.filter(price__gte=search_dictionary["min_value"])
        if search_dictionary["max_value"] != None:
            result = result.filter(price__lte=search_dictionary["max_value"])
        if search_dictionary["sort"] == "LST":
            result = result.order_by("-id")
        elif search_dictionary["sort"] == "LTH":
            result = result.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
        elif search_dictionary["sort"] == "HTL":
            result = result.order_by("-price")
        return result
    
    if search_dictionary["search_type"] == "seller":
        result = Products.objects.select_related("supplier").filter(supplier__slug=search_dictionary["seller_slug"])
        if search_dictionary["keyword"] != "" and search_dictionary["keyword"] != "None" and search_dictionary["keyword"] != None:
            result = result.filter(Q(product_name__icontains=search_dictionary["keyword"])|Q(description__icontains=search_dictionary["keyword"])|Q(supplier__company_name__icontains=search_dictionary["keyword"])|Q(keywords__icontains=search_dictionary["keyword"]))
        if search_dictionary["subcategorys"] != []:
            result = result.filter(sub_category__slug__in=search_dictionary["subcategorys"])
        if search_dictionary["selected_brands"] != []:
            result = result.filter(brand__in=search_dictionary["selected_brands"])
        if search_dictionary["min_value"] != "None" and search_dictionary["min_value"] != "" and search_dictionary["min_value"] != None:
            result = result.filter(price__gte=search_dictionary["min_value"])
        if search_dictionary["max_value"] != "None" and search_dictionary["max_value"] != "" and search_dictionary["max_value"] != None:
            result = result.filter(price__lte=search_dictionary["max_value"])
        if search_dictionary["sort"] == "LST":
            result = result.order_by("-id")
        elif search_dictionary["sort"] == "LTH":
            result = result.annotate(zero_price=Case(When(price=0, then=Value(9999999)),default=F('price'),output_field=IntegerField(),), ).order_by('zero_price')
        elif search_dictionary["sort"] == "HTL":
            result = result.order_by("-price")
        elif search_dictionary["sort"] == "popular":
            result = result.order_by("-clicks")
        return result
        

def search_template_middlewares(products, search_type):
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

    search_seller = []
    search_subcategory = []
    brands = []
    for p in products:
        if not p.supplier in search_seller:
            search_seller.append(p.supplier)    
        if not p.sub_category in search_subcategory:
            search_subcategory.append(p.sub_category)
        if p.price < min_price_of_all_products:
            min_price_of_all_products = p.price
        if p.price > max_price_of_all_products:
            max_price_of_all_products = p.price
        if p.brand != None and not p.brand in brands:
            brands.append(p.brand)

    # Now filter by category
    if category != None:
        products = products.filter(category=category)

    # Now filter by brands
    if len(selected_brands) != 0:
        products = products.filter(brand__in=selected_brands)

    # Pagination

    pag = Paginator(products,16)
    page_number = request.GET.get("page")

    try:
        page_obj = pag.page(page_number)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)

    context["products_count"] = products.count()

    context["slug"] = slug
    context["current_category"] = category
    context["pag"] = page_obj
    context["sub_category"] = Subcategory.objects.filter(category=category)

    context["sub_categ"] = request.GET.get("sub_categ")
    context["keyword"] = keyword
    context["min_value"] = min_value
    context["max_value"] = max_value
    context["sort"] = sort

    context["min_price_of_all_products"] = min_price_of_all_products
    context["max_price_of_all_products"] = max_price_of_all_products
    context["supplier"] = search_seller
    context["subcategory"] = search_subcategory
    context["brands"] = brands 


def main_search(request):
    search_dictionary = {}
    search_dictionary["keyword"] = request.GET.get('keyword')
    search_dictionary["sort"] = request.GET.get("sort")
    search_dictionary["min_value"] = request.GET.get("min_value")
    search_dictionary["max_value"] = request.GET.get("max_value")

    search_dictionary["subcategorys"] = request.GET.getlist('sub_categ')
    search_dictionary["selected_brands"] = request.GET.getlist("brand")
    search_dictionary["sellers"] = request.GET.getlist('seller')
    search_dictionary["selected_business"] = request.GET.getlist('business') 
    search_dictionary["search_type"] = "normal"
    print(search_dictionary)
    products = search_manager(search_dictionary)
    
    context = {} 

    context['products'] = products

    search_seller = []
    search_subcategory = []
    for p in products:
        if not p.supplier in search_seller:
            search_seller.append(p.supplier)    
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

    context["suppliers"] = search_seller
    context["subcategory"] = search_subcategory
    context["keyword"] = search_dictionary["keyword"]
    # from search_dictionary['keyword'] find me a list of subcategories
    all_filters = Products.objects.select_related("supplier").select_related("sub_category").filter(Q(product_name__icontains=search_dictionary["keyword"])|Q(description__icontains=search_dictionary["keyword"])|Q(supplier__company_name__icontains=search_dictionary["keyword"])|Q(keywords__icontains=search_dictionary["keyword"]))
    all_subcategories = []
    all_sellers = []
    all_brands = []
    all_business = []
    max_price_of_all_products = Products.objects.filter(Q(product_name__icontains=search_dictionary["keyword"])).aggregate(max_price=Max('price'))['max_price'] 
    min_price_of_all_products = Products.objects.filter(Q(product_name__icontains=search_dictionary["keyword"])).filter(price__gt=0).aggregate(min_price=Min('price'))['min_price'] 
    context["min_price_of_all_products"] = min_price_of_all_products
    context["max_price_of_all_products"] = max_price_of_all_products

    for subs in all_filters:
        if subs.sub_category not in all_subcategories:
            all_subcategories.append(subs.sub_category)
        if subs.supplier not in all_sellers:
            all_sellers.append(subs.supplier)
        if subs.brand not in all_brands:
            all_brands.append(subs.brand)
        if subs.supplier.secondary_business not in all_business:
           all_business.append(subs.supplier.secondary_business)
   
    for b in all_brands:
        if b == "Not Mentioned":
            all_brands.remove(b)
            all_brands.append(b)
    context["all_subcategories"] = all_subcategories
    context["all_sellers"] = all_sellers
    context["all_brands"] = all_brands
    context["all_business"] = all_business
    context["selected_subcats"] = search_dictionary["subcategorys"]
    context["selected_suppliers"] = search_dictionary["sellers"]
    context["selected_brands"] = search_dictionary["selected_brands"]
    context["selected_business"] = search_dictionary["selected_business"]
    print(context['selected_business']) 
    pagination_string_next = ""
    pagination_string_prev = ""
    if context["pag"].has_next(): 
        pagination_string_next = ""
        pagination_string_next += "?page=" + str(context["pag"].next_page_number())
        pagination_string_next += "&keyword=" + search_dictionary["keyword"]
        if search_dictionary["sellers"] != None:
            for supplier in search_dictionary["sellers"]:
                pagination_string_next += "&seller=" + supplier
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
        pagination_string_prev += "&keyword=" + search_dictionary["keyword"]
        if search_dictionary["sellers"] != None:
            for supplier in search_dictionary["sellers"]:
                pagination_string_prev += "&seller=" + supplier
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
    return render(request, "sanjog/searchpage.html", context) 
    

def sellerpage_livesearch(request, slug):
    if request.is_ajax():
        res = None
        prods = request.GET.get('prod')
        results = Products.objects.select_related("supplier").filter(supplier__slug=slug).filter(Q(product_name__icontains=prods)|Q(keywords__icontains=prods)|Q(description__icontains=prods))
        if len(results)>0 and len(prods)>0:
            data = []
            for pos in results:
                item = {
                    'pk':pos.pk,
                    'name':pos.product_name,
                    'slug':pos.slug,
                }
                data.append(item)
            res = data[:10]
        else:
            res = "No products found ..."
        return JsonResponse({'data':res})
    return JsonResponse({})

def trending_search(request):
    context = {}
    products = Products.objects.all().order_by("-clicks")[:100]
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
    

