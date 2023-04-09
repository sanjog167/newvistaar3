from django.urls import path

from account import views
from .views import *

app_name = 'products'

urlpatterns = [
    
    path('<int:id>/<slug:slug>/', product_detail,name='product_detail'),
    path('category/all', all_category_detail,name='all_category_detail'),
    path('category/<int:id>/<slug:slug>/', category_detail,name='category_detail'),
    path('subcategory/<int:id>/<slug:slug>/', subcategory_detail,name='subcategory_detail'),
    path('submit_product', submit_product,name='submit_product'),
    path('get_best_price/<int:id>', get_best_price, name='get_best_price'),
    path('get_subcategorys/<int:id>', get_subcategorys, name='get_subcategorys'),
    path('edit_product/<int:id>/', edit_product, name='edit_product'),

    #ath("search/", SearchView.as_view(), name="search"),
    path("livesearch/", livesearch, name="livesearch"),
    path("sellerpage_livesearch/<slug:slug>/", sellerpage_livesearch, name="sellerpage_livesearch"),
    path("requirements_livesearch/", post_requirements_livesearch, name="post_requirements_livesearch"),
    path("keywords_data/", keyword_data,name="keyword_data"),
    path("alert_supplier/", alert_supplier,name="alert_supplier"),
    path("test/", main_search,name="test"),
    path("trending/", trending_search,name="trending_search"),
]

