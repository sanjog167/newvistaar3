from ftplib import all_errors
from unicodedata import name
from django.db import reset_queries
from django.shortcuts import redirect, render
from django.contrib import messages
from django.shortcuts import render, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.shortcuts import get_object_or_404
from .forms import LeadsEditForm, MyPasswordChangeForm, UserRegistrationForm, UserEditForm, ProfileEditForm, CompanyForm, EditCompanyInfoForm, CustomUserCreationForm, SupplierForm, SupplierFormEdit
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from suppliers.models import Company, Supplier
from products.models import Products
from request.models import SellerRequest
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_text,force_str,DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage, send_mass_mail
from django.conf import settings as conf_settings
from django.utils.text import slugify
from django.db.models import Value, CharField
import os
from vistaar.settings import MEDIA_ROOT

from django.contrib.admin.views.decorators import staff_member_required
import qrcode
from PIL import Image
from pathlib import Path

import json

from itertools import chain

# from openpyxl import Workbook

# Create your views here.
def send_supplier_verification_email(user,request):
    current_site = get_current_site(request)
    email_subject = f"{user.username} applied for seller account!"
    email_body = render_to_string('account/seller_notification.html',{
        'user':user,
    })
    
    email = EmailMessage(subject=email_subject,body=email_body,from_email=conf_settings.EMAIL_FROM_USER,to=["email_test_vistaar@anukul.com.np"])

    email.send()
#Activation email - SEND
def send_action_email(user,request):
    current_site = get_current_site(request)
    email_subject = "Action Required: Verify Your Email Address on Vistaar Trade"
    email_body = render_to_string('account/activate.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user),
    })
    
    email = EmailMessage(subject=email_subject,body=email_body,from_email=conf_settings.EMAIL_FROM_USER,to=[user.email])

    email.send()
    
    
#Lead notification Email
def send_lead_email(user,supplier,product,request, quantity_required):
    email_subject = f"{product.product_name} Inquiry from Vistaar Trade" 
    email_body = render_to_string('supplier/new_lead.html',{
        'user':user,
        'supplier':supplier,
        'product':product,
        'quantity': quantity_required,
    })
    
    email = EmailMessage(subject=email_subject,body=email_body,from_email=conf_settings.EMAIL_FROM_USER,to=[supplier.email,supplier.user.email])
    email.send()
def send_contact_view_email(user,supplier,product,request):
    email_subject = 'Vistaar - You have a new notification!'
    email_body = render_to_string('supplier/user_viewed_contact.html',{
        'user':user,
        'supplier':supplier,
        'product':product,
    })
    
    email = EmailMessage(subject=email_subject,body=email_body,from_email=conf_settings.EMAIL_FROM_USER,to=[supplier.email,supplier.user.email])
    email.send()
def check_email(request):
    user = User.objects.get(id=21)
    send_action_email(user,request)

    return redirect('home')
def user_creation_form(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password
                )
            user.save()
            
            user.profile.mobile_number = phone_number
            
            user.profile.save()
            
            send_action_email(user,request)
            
            messages.success(request, 'Your account has been created. Login to continue!')
            user_email = user.email 
            return render(request, 'sanjog/verifyemail.html', {'user_email':user_email})
        else:
            error_json = form.errors.as_json()
            parsed_json = json.loads(error_json)
            for key, value in parsed_json.items():
                messages.error(request, value[0]['message'], extra_tags=key)
            return render(request, 'account/user_register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        context = {
            "form": form,
        }
        return render(request, 'account/user_register.html', context)

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name  = request.POST['last_name']
        username  = request.POST['username']
        email  = request.POST['email']
        password  = request.POST['password']
        confirm_password  = request.POST['confirm_password']
        phone_number = request.POST['phone_number']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken. Try a different one!')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered!')
                return redirect('register')
            else:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password
                )
                user.save()
                
                user.profile.mobile_number = phone_number
                
                user.profile.save()
                
                #send_action_email(user,request)
                
                messages.success(request, 'Your account has been created. Login to continue!')
                
                return redirect('login')
        else:
            messages.error(request, 'Password fields do not match!')
            return redirect('register')
    else:
        return render(request,'account/register.html')
    

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # check if user exists
        try:
            get_user = User.objects.get(username=username) 
        except:
            messages.error(request, f"{username} does not exist. Please register to continue.")
            return redirect('login')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.profile.email_verified == False:
                user_email = user.email
                messages.error(request, 'Please verify your email address to continue.')
                return render(request, 'sanjog/verifyemail.html', {'user_email':user_email})
            if user.is_active:
                login(request, user)
                messages.success(request, 'Logged In Successfully!')
                if request.GET.get("next") != None:
                    return redirect(request.GET.get("next"))
                return redirect('home')
            else:
                messages.error(request, 'Disabled account')
                return redirect('login')
        else:
            messages.error(request, f"password does not match. Please enter correct password to continue.")
            return redirect('login')
    else:
        return render(request, 'sanjog/login.html')

@login_required
def create_rfq_leads(request):
    if request.method == 'POST':
        keyword = request.POST['keyword']
        description = request.POST['description']
        quantity = request.POST['quantity']
        subcategory = request.POST['subcategory']
        user = request.user
        mobile_number = request.user.profile.mobile_number
        products = Products.objects.select_related('supplier').filter(sub_category=subcategory).filter(Q(product_name__icontains=keyword) | Q(description__icontains=keyword))
        messages = ()
        rfq_leads_list = []
        for product in products:
            context = {
                'user': user,
                'mobile_number': mobile_number,
                'product': product,
                'keyword': keyword,
                'description': description,
                'quantity': quantity, 
            }
            rfq_lead = RFQ_leads(
                seller=product.supplier,
                buyer=user,
                product=product,
                quantity_required=quantity,
                request_description=description,
            )
            rfq_leads_list.append(rfq_lead)
            email_payload = render_to_string('sanjog/rfq_leads.html', context) 
            messages += ((f"{product} Inquiry from Vistaar Trade", email_payload, conf_settings.EMAIL_FROM_USER, [product.supplier.contact_email]),)
        email_payload = (
                f"User {user.username} wants to buy {keyword}",
                description,
                conf_settings.EMAIL_FROM_USER,  # From email address
            )
            # now create rfq lead
        send_mass_mail(messages, fail_silently=False)
        RFQ_leads.objects.bulk_create(rfq_leads_list)
        print(messages)
    else:
        return redirect('home') 
    return redirect('home') 

@login_required
def post_requirements(request):
    if request.method == 'POST':

        current_user = request.user.username
        buyer = User.objects.get(username=current_user)
        try:
            product_attribute = request.POST['product']
            product = Products.objects.filter(Q(product_name__icontains=product_attribute) | Q(description__icontains=product_attribute))
        except Products.DoesNotExist:
            product = None
        quantity_required = request.POST['quantity']
        request_description = request.POST['description']
        for pr in product:
            try:
                supplier_user = User.objects.get(username=pr.supplier.user.username)
                supplier = Supplier.objects.get(user=supplier_user)
            except Supplier.DoesNotExist:
                supplier = None



            rfq_leads = RFQ_leads(seller=supplier, buyer=buyer, product=pr,
                                        quantity_required=quantity_required,
                                        request_description=request_description)

            rfq_leads.save()
            #send_lead_email(current_user,supplier,pr,request)
        return redirect('home')
    else:
        return render(request, 'account/post_requirements.html')


@login_required
def dashboard(request):
    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    all_products = Products.objects.filter(supplier = current_supplier)
    all_products_count = all_products.count()
    views = all_products.aggregate(models.Sum('clicks'))['clicks__sum']

    latest_buyleads = Primary_leads.objects.filter(seller = current_supplier)[:3]
    all_buyleads_count = Primary_leads.objects.filter(seller=current_supplier).count()

    trending_products = Products.objects.filter(supplier=current_supplier).order_by('-clicks')[:4]
    trending_names = []
    trending_clicks = []
    clicks_count = 0

    primary_leads = Primary_leads.objects.filter(seller=current_supplier).order_by("created")
    rfq_leads = RFQ_leads.objects.filter(seller=current_supplier).order_by("created")
    rfq_leads_count = rfq_leads.count()
    premium_leads = Premium_leads.objects.filter(seller=current_supplier).order_by("created")
    
    all_leads = chain(primary_leads,rfq_leads,premium_leads)

    
    customer_list = []
    for list in all_leads:
        if list.buyer in customer_list:
            a = 1
        else:
            customer_list.append(list.buyer)

    for p in trending_products:
        trending_names.append(str(p.product_name[:5]))
        trending_clicks.append(p.clicks)
        clicks_count += p.clicks

    return render(request,
                'sanjog/dashboard.html',
                {'section': 'dashboard','current_profile': current_profile,
                'current_supplier':current_supplier,'leads':latest_buyleads,'leads_count':all_buyleads_count,
                'trending':trending_products,'trending_names':trending_names,'trending_count':trending_clicks,'trending_total_count':clicks_count,
                'views':views,'all_count':all_products_count,'customer_list':customer_list,'rfq_count':rfq_leads_count}
                )
@login_required
def register_supplier(request):
    current_user = request.user
    context = {}
    form = SupplierForm(request.POST)
    context['form'] = form
    if ('submit' in request.POST):
        if current_user.profile.linked == True:
            messages.error(request, 'You already applied for a supplier account')
            context['mobile_number'] = Profile.objects.get(user=current_user).mobile_number
            context['email'] = current_user.email 
            context['form'] = form
            return render(request, 'account/test_supplier_form.html', context)   
        if form.is_valid():
            form_data = request.POST
            #create_supplier(form_data,current_user)
            form_data = form.save(commit=False)
            form_data.user = request.user
            form_data.mobile_number = Profile.objects.get(user=current_user).mobile_number
            form_data.email = current_user.email
            form_data.slug = slugify(form_data.company_name)
            form_data.save()
            profile = Profile.objects.get(user=current_user)
            generate_qr(current_user.supplier)
            current_user.profile.linked = True
            current_user.save()
            ## supplier disabled until verified by admin from django dashboard
            profile.account_type = 'Supplier1'
            profile.save()
            send_supplier_verification_email(current_user, request)
            SellerRequest.objects.create(user=current_user) 
            #return render(request, 'sanjog/temporary_seller_detail.html') 
            #return render(request, 'account/verifying_you.html')
            return redirect("home")
        context['mobile_number'] = Profile.objects.get(user=current_user).mobile_number
        context['email'] = current_user.email 
        context['form'] = form
        error_json = form.errors.as_json()
        parsed_json = json.loads(error_json)
        for key, value in parsed_json.items():
            messages.error(request, value[0]['message'], extra_tags=key)
        return render(request, 'account/test_supplier_form.html', context)


    else:
        form = SupplierForm(request.POST)
        context['mobile_number'] = Profile.objects.get(user=current_user).mobile_number
        context['email'] = current_user.email 
        context['form'] = form
        return render(request, 'account/test_supplier_form.html', context)

@login_required
def company_profile(request):
    context = {}
    supplier = Supplier.objects.get(user=request.user)
#    try:
#        current_supplier = Supplier.objects.get(user=request.user)
#    except Supplier.DoesNotExist:
#        current_supplier = None
#
#    current_company = Company.objects.get_or_create(supplier=current_supplier)
#
#
    form = SupplierFormEdit(request.POST, instance = supplier)
    if ("submit" in request.POST):
        if form.is_valid():
            if "profile_picture" in request.FILES:
                form_data.profile_picture = request.FILES['profile_picture']
            form_data = form.save(commit=False)
            form_data.save()
            print("form was validated and updated")
            return redirect('company_profile') 
            #return render(request, 'account/verifying_you.html')
        else:
            error_json = form.errors.as_json()
            parsed_json = json.loads(error_json)
            for key, value in parsed_json.items():
                messages.error(request, value[0]['message'], extra_tags=key)
            context['form'] = form
            context['mobile_number'] = Profile.objects.get(user=request.user).mobile_number
            context['email'] = request.user.email 
            context['name'] = request.user.supplier.name 
            context['company_name'] = request.user.supplier.company_name
            context['profile_picture'] = request.user.supplier.profile_picture
            # form placeholder values add
            form['phone_number'].field.widget.attrs['placeholder'] = request.user.supplier.phone_number
            form['phone_number'].field.widget.attrs['value'] = request.user.supplier.phone_number
            form['establishment_year'].field.widget.attrs['placeholder'] = request.user.supplier.establishment_year
            form['establishment_year'].field.widget.attrs['value'] = request.user.supplier.establishment_year
            form['ceo_name'].field.widget.attrs['placeholder'] = request.user.supplier.ceo_name
            form['ceo_name'].field.widget.attrs['value'] = request.user.supplier.ceo_name
            form['website'].field.widget.attrs['placeholder'] = request.user.supplier.website
            form['website'].field.widget.attrs['value'] = request.user.supplier.website
            form['state'].field.widget.attrs['placeholder'] = request.user.supplier.state
            form['state'].field.widget.attrs['value'] = request.user.supplier.state
            form['address1'].field.widget.attrs['placeholder'] = request.user.supplier.address1
            form['address1'].field.widget.attrs['value'] = request.user.supplier.address1
            form['address2'].field.widget.attrs['placeholder'] = request.user.supplier.address2
            form['address2'].field.widget.attrs['value'] = request.user.supplier.address2
            form['exim'].field.widget.attrs['placeholder'] = request.user.supplier.exim
            form['exim'].field.widget.attrs['value'] = request.user.supplier.exim
            form['pan'].field.widget.attrs['placeholder'] = request.user.supplier.pan
            form['pan'].field.widget.attrs['value'] = request.user.supplier.pan
            form['vat'].field.widget.attrs['placeholder'] = request.user.supplier.vat
            form['vat'].field.widget.attrs['value'] = request.user.supplier.vat
            form['contact_name'].field.widget.attrs['placeholder'] = request.user.supplier.contact_name
            form['contact_name'].field.widget.attrs['value'] = request.user.supplier.contact_name
            form['contact_phone'].field.widget.attrs['placeholder'] = request.user.supplier.contact_phone
            form['contact_phone'].field.widget.attrs['value'] = request.user.supplier.contact_phone
            form['contact_email'].field.widget.attrs['placeholder'] = request.user.supplier.contact_email
            form['contact_email'].field.widget.attrs['value'] = request.user.supplier.contact_email
            # form['state'] has options i want to preselect options from database using request.user.supplier.state
            context['state_value'] = request.user.supplier.state
            context['selected_secondary_business'] = list(request.user.supplier.secondary_business)
            return render(request,'sanjog/profile.html',context)
    context['form'] = form
    context['mobile_number'] = Profile.objects.get(user=request.user).mobile_number
    context['email'] = request.user.email 
    context['name'] = request.user.supplier.name 
    context['company_name'] = request.user.supplier.company_name
    context['profile_picture'] = request.user.supplier.profile_picture
    # form placeholder values add
    form['phone_number'].field.widget.attrs['placeholder'] = request.user.supplier.phone_number
    form['phone_number'].field.widget.attrs['value'] = request.user.supplier.phone_number
    form['establishment_year'].field.widget.attrs['placeholder'] = request.user.supplier.establishment_year
    form['establishment_year'].field.widget.attrs['value'] = request.user.supplier.establishment_year
    form['ceo_name'].field.widget.attrs['placeholder'] = request.user.supplier.ceo_name
    form['ceo_name'].field.widget.attrs['value'] = request.user.supplier.ceo_name
    form['website'].field.widget.attrs['placeholder'] = request.user.supplier.website
    form['website'].field.widget.attrs['value'] = request.user.supplier.website
    form['state'].field.widget.attrs['placeholder'] = request.user.supplier.state
    form['state'].field.widget.attrs['value'] = request.user.supplier.state
    form['address1'].field.widget.attrs['placeholder'] = request.user.supplier.address1
    form['address1'].field.widget.attrs['value'] = request.user.supplier.address1
    form['address2'].field.widget.attrs['placeholder'] = request.user.supplier.address2
    form['address2'].field.widget.attrs['value'] = request.user.supplier.address2
    form['exim'].field.widget.attrs['placeholder'] = request.user.supplier.exim
    form['exim'].field.widget.attrs['value'] = request.user.supplier.exim
    form['pan'].field.widget.attrs['placeholder'] = request.user.supplier.pan
    form['pan'].field.widget.attrs['value'] = request.user.supplier.pan
    form['vat'].field.widget.attrs['placeholder'] = request.user.supplier.vat
    form['vat'].field.widget.attrs['value'] = request.user.supplier.vat
    form['contact_name'].field.widget.attrs['placeholder'] = request.user.supplier.contact_name
    form['contact_name'].field.widget.attrs['value'] = request.user.supplier.contact_name
    form['contact_phone'].field.widget.attrs['placeholder'] = request.user.supplier.contact_phone
    form['contact_phone'].field.widget.attrs['value'] = request.user.supplier.contact_phone
    form['contact_email'].field.widget.attrs['placeholder'] = request.user.supplier.contact_email
    form['contact_email'].field.widget.attrs['value'] = request.user.supplier.contact_email
    # form['state'] has options i want to preselect options from database using request.user.supplier.state
    context['state_value'] = request.user.supplier.state
    context['selected_secondary_business'] = list(request.user.supplier.secondary_business)
    
   
    
    return render(request,'sanjog/profile.html',context)
                

@login_required
def lead_manager(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    sent_messages = Lead_messages.objects.filter()

    return render(request,
                'dashboard/lead_manager.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})

@login_required
def manage_products(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None
    products = Products.objects.filter(supplier=current_supplier)

    return render(request,
                'sanjog/products.html',
                {'section': 'dashboard','current_profile': current_profile,
                 'current_supplier':current_supplier,
                 'products': products})


@login_required
def buy_leads(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    primary_leads = Primary_leads.objects.filter(seller=current_supplier).order_by("created").exclude(consumed=True).annotate(temp_field=Value('Primary_leads', output_field=CharField()))
    rfq_leads = RFQ_leads.objects.filter(seller=current_supplier).order_by("created").exclude(consumed=True).annotate(temp_field=Value('RFQ_leads', output_field=CharField())) 
    premium_leads = Premium_leads.objects.filter(seller=current_supplier).order_by("created").exclude(consumed=True).annotate(temp_field=Value('Premium_leads', output_field=CharField()))
    
    cprimary_leads = Primary_leads.objects.filter(Q(consumed=True) & Q(seller=current_supplier)).order_by("created")
    crfq_leads = RFQ_leads.objects.filter(Q(consumed=True) & Q(seller=current_supplier)).order_by("created")
    cpremium_leads = Premium_leads.objects.filter(Q(consumed=True) & Q(seller=current_supplier)).order_by("created")
    
    all_leads = sorted(chain(primary_leads,rfq_leads,premium_leads) , key=lambda instance: instance.created)
    consumed_leads = sorted(chain(cprimary_leads,crfq_leads,cpremium_leads) , key=lambda instance: instance.created)
    if request.method == "POST":
        leadsid = request.POST['lead_id']
        lead_type = request.POST['lead_type']
        if lead_type == "Primary_leads":
            ins = Primary_leads.objects.get(id=leadsid)
            ins.consumed = True
            ins.save()
        elif lead_type == "RFQ_leads":
            ins = RFQ_leads.objects.get(id=leadsid)
            ins.consumed = True
            ins.save()
        elif lead_type == "Premium_leads":
            ins = Premium_leads.objects.get(id=leadsid)
            ins.consumed = True
            ins.save()
        return redirect('buy_leads')
            
    return render(request,
                'sanjog/leads.html',
                {'section': 'dashboard','current_profile': current_profile,
                 'prim_leads': primary_leads,
                 'rfq_leads':rfq_leads,
                 'prem_leads':premium_leads,
                 'all_leads':all_leads,
                 'consumed_leads':consumed_leads,
                 })


@login_required
def edit_leads(request, id):
    lead = Primary_leads.objects.get(pk=id)

    if request.method == 'POST':
        lead_edit_form = LeadsEditForm(instance=lead,
                                    data=request.POST)
        if lead_edit_form.is_valid():
            lead_edit_form.save()
    else:
        lead_edit_form = LeadsEditForm(instance=lead)
    return render(request,
                  'dashboard/edit_leads.html',
                  {'lead_edit_form': lead_edit_form})


@login_required
def collect_payments(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/collect_payments.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})

@login_required
def catalog_view(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/catalog_view.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})

@login_required
def photos_docs(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/photos&docs.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})


@login_required
def bills_invoice(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/bill&invoice.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})


@login_required
def buyer_tools(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/buyer_tools.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})


@login_required
def settings(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/settings.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                    data=request.POST,
                                    files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        
        if not request.user.profile.email_verified:
            send_action_email(request.user,request)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


def generate_qr(new_supplier):
# taking image which user wants
# in the QR code center

    Logo_link = 'static/images/faviconbg4.png'

    logo = Image.open(Logo_link)

# taking base width
    basewidth = 100

# adjust image size
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(
	error_correction=qrcode.constants.ERROR_CORRECT_H)


# taking url or text
    url = 'vistaartrade.com/'+'supplier/'+ str(new_supplier.slug)

# adding URL or text to QRcode
    QRcode.add_data(url)

# generating QR code
    QRcode.make()

# taking color name from user
    QRcolor = '#00917c'

# adding color to QR code
    QRimg = QRcode.make_image(
	fill_color=QRcolor, back_color="white").convert('RGB')

# set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
	        (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)


    destination = ''.join(['media/suppliers/',str(new_supplier.id),'/','qr_code.png'])
    if not os.path.exists(''.join(['media/suppliers/',str(new_supplier.id)])):
        os.makedirs(''.join(['media/suppliers/',str(new_supplier.id)]))
    # save the QR code generated
    QRimg.save(destination)

    new_supplier.qr_code = ''.join(['suppliers/',str(new_supplier.id),'/','qr_code.png'])
    new_supplier.save()

    print('QR code generated!')

def qr_update():
    all_suppliers = Supplier.objects.all()

    for sup in all_suppliers:
        path = os.path.join(MEDIA_ROOT, 'suppliers/', str(sup.id))
        os.makedirs(path,exist_ok=True)
        
        generate_qr(sup)
    
def create_supplier(form_data,current_user):
    new_supplier = Supplier.objects.create(user=current_user,
                                                name = current_user.first_name,
                                                company_name = form_data['company-name'],
                                                mobile_number = form_data['company-phone'],
                                                establishment_year = form_data['estdyear'],
                                                ceo_name = form_data['ceo-name'],
                                                email = form_data['company-email'],
                                                website = form_data['website'],
                                                contact_name = form_data['contact-name'],
                                                contact_phone = form_data['contact-phone'],
                                                contact_email = form_data['contact-email'],
                                                state = form_data['state'],
                                                address1 = form_data['address1'],
                                                address2 = form_data['address2'],
                                                pan = form_data['pan'],
                                                vat = form_data['vat']   )

    
    new_supplier.save()

    path = os.path.join(MEDIA_ROOT, 'suppliers/', str(new_supplier.id))
    os.makedirs(path,exist_ok=True)

    workbook = Workbook()
    workbook_dest = os.path.join(path,"data.xlsx")
    workbook.save(filename=workbook_dest)
    
    generate_qr(new_supplier)

    current_user.linked = True
    current_user.save()

    user_profile = Profile.objects.get(user=current_user)
    user_profile.linked = True
    user_profile.save()
    

# @login_required
# def register_supplier(request):
#     current_user = request.user

#     if request.method == 'POST':
#         form_data = request.POST

#         create_supplier(form_data,current_user)

#         profile = Profile.objects.get(user=current_user)
#         profile.account_type = 'Supplier1'
#         profile.save()

#         return render(request, 'account/verifying_you.html')

#     else:

#         return render(request,'account/become-a-seller.html')


@login_required
def edit_company_info(request):
    if request.method == 'POST':
        company_info_form = EditCompanyInfoForm(instance=request.user.supplier,
                                 data=request.POST)
        if company_info_form.is_valid():
            company_info_form.save()
    else:
        company_info_form = EditCompanyInfoForm(instance=request.user.supplier)
    return render(request,
                  'dashboard/edit_company_info.html',
                  {'company_info_form': company_info_form})


@login_required
def edit_business_profile(request):
    if request.method == 'POST':
        business_profile_form = EditBusinessProfileForm(instance=request.user.supplier,
                                 data=request.POST)
        if business_profile_form.is_valid():
            business_profile_form.save()
    else:
        business_profile_form = EditBusinessProfileForm(instance=request.user.supplier)
    return render(request,
                  'dashboard/edit_company_info.html',
                  {'company_info_form': business_profile_form})


@login_required
def change_password(request):
    if request.method == 'POST':
        change_password_form = MyPasswordChangeForm(user=request.user, data=request.POST)
        if change_password_form.is_valid():
            change_password_form.save()
            # This will update the session and we won't be logged out after changing the password
            update_session_auth_hash(request, change_password_form.user)
            messages.success(request, 'Your password has been updated!')
            return redirect('password_change')
        else:
            messages.success(request, 'Something went wrong. Please try again.')
            return redirect('password_change')
    else:
        change_password_form = MyPasswordChangeForm(user=request.user)
    context = {
               'change_password_form':change_password_form,
               }
    return render(request, 'account/password_change_form.html', context)
    

#Activation email - Verification
def activate_user(request,uidb64,token):
    
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
        
    except Exception as e:
        user = None
        
    if user and generate_token.check_token(user,token):
        user.profile.email_verified=True
        user.save()
        
        messages.add_message(request, messages.SUCCESS, 'Your account has been successfully activated!')
        
        return redirect(reverse('home'))
        
    return render(request,'account/activation-failed.html',{'curuser':user,'userid':uid})

def delete_product(request):
    name = request.POST['id']
    product = Products.objects.get(product_name=name)
    product.delete()
    return redirect('manage_products')



@staff_member_required
def crm_view(request):
    if request.method == 'POST':
        phone_number = request.POST['number']
        url = f"https://api.whatsapp.com/send?phone=977{phone_number}"
        return redirect(url)
    return render(request, 'crm.html')     