from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from products.models import Category

class SellerRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    time = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.user.username

class SubCategoryRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.category} > {self.sub_category}"