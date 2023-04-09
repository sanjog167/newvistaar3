from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from .models import Category,Products,Subcategory
from django.db import models
# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    #list_display = ['product_name', 'slug', 'description', 'available', 'created', 'updated']
    prepopulated_fields = {'slug': ('product_name',)}
    list_filter = ('supplier','category', )
    search_fields = ['product_name', ]
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
    
    
@admin.register(Subcategory)
class ProductAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('title',)}


