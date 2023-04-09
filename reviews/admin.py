from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ReviewRating


# Register your models here.
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id','uname','review','rating','product')
admin.site.register(ReviewRating, ReviewAdmin)