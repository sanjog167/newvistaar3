from django.shortcuts import render
from products.models import Category
from request.forms import SubCategoryRequestForm
from request.models import SubCategoryRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings as conf_settings

def send_subcategory_request_email(user,request, category):
    email_subject = f"{user.username} requested for new subcategory!"
    email_body = render_to_string('account/subcategory_recommendation_notification.html',{
        'user':user,
        'category': category,
    })
    
    email = EmailMessage(subject=email_subject,body=email_body,from_email=conf_settings.EMAIL_FROM_USER,to=["email_test_vistaar@anukul.com.np"])

    email.send()


@login_required
def subcategory_request(request):
    context = {}
    print(request.user)
    context['form'] = SubCategoryRequestForm()
    print(request.POST)
    if "submit" in request.POST:
        form = SubCategoryRequestForm(request.POST)
        cat_id = Category.objects.get(id=request.POST['category'])
        user = User.objects.get(username=request.user)
        SubCategoryRequest.objects.create(category=cat_id, user=user, sub_category=request.POST['subcategory']) 
        send_subcategory_request_email(request.user, request, cat_id.title)
        return render(request, 'sanjog/subcategory_request.html', context)
    else:
        context['categorys'] = Category.objects.all() 
    return render(request, 'sanjog/subcategory_request.html', context)