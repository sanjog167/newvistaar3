from django.urls import path
from django.contrib.auth import views as auth_views
from request.views import *


urlpatterns = [
    path('subcategory/', subcategory_request, name='subcategory_request'),
]
