from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import ReviewRating,Products
from .forms import ReviewForm
from django.contrib import messages
from django.db.models import Q


# Create your views here.

#review
@login_required
def submit_review(request,product_id):
    print("goodogood")
    print(request.user,product_id)
    product = Products.objects.get(id=product_id)
    print(product)
    url = request.META.get('HTTP_REFERER')#storing the current url of the page
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)#to check if the same user has reviewed the same product or not
            print(reviews)
            print(request.POST)
            form = ReviewForm(request.POST,instance=reviews)#used for updating existing review data with new review data
            form.save()
            messages.success(request, 'Your reviews has been updated!!')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()#creating object of review
                data.review = form.cleaned_data['review']
                data.uname = form.cleaned_data['uname']
                data.email = form.cleaned_data['email']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.rating = 4
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted')
                print("Thank you")
                return redirect(url)
            # return render(request, 'review/review.html')
    # messages.error(request, 'You must be login to provide a review.')
        return redirect(url)