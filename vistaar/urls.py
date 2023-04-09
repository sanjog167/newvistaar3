"""vistaar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.urls.conf import re_path
from products.views import HomeView,category_detail,privacy_policy,terms_conditions,about_us,seller_become,email_verify,seller_page,seller_leads
from django.conf import settings
from django.conf.urls.static import static
from products.views import filter_data_sort,filter_data_price
from reviews.views import submit_review


urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('', HomeView.as_view(), name='home'),
    path('products/', include('products.urls')),
    path('supplier/', include('suppliers.urls')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('<int:id>/<slug:slug>/', category_detail,name='category_detail'),
    path('privacy-policy', privacy_policy,name='privacy_policy'),
    path('terms-conditions', terms_conditions,name='terms_conditions'),
    path('seller-page', seller_page,name='seller_page'),
    path('about', about_us,name='about_us'),
    path('email-verify', email_verify,name='email_verify'),
    path('seller-leads', seller_leads,name='seller_leads'),
    path('seller', seller_become,name='seller_become'),
    path("filter-data-sort/",filter_data_sort,name="filter_data_sort"),
    path("filter-data-price/",filter_data_price,name="filter_data_price"),
    path('submit_review/<int:product_id>',submit_review,name='submit_review'),
    path('request/', include('request.urls')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
