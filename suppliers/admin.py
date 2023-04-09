from django.contrib import admin
from .models import Supplier, Company, CompanyAddress, CompanyStatutory
# Register your models here.

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('company_name',)}
admin.site.register(Company)
admin.site.register(CompanyAddress)
admin.site.register(CompanyStatutory)