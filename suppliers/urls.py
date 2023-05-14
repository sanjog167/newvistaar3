from django.urls import path
from .views import all_suppliers, new_supplier_detail_ajax

app_name = 'suppliers'

urlpatterns = [
    
    path('<slug:slug>/', new_supplier_detail_ajax,name='supplier_detail'),
    path('all-suppliers', all_suppliers,name='all-suppliers'),

]
