from django.urls import path
from myshop import views
app_name ='myshop'
urlpatterns=[
    path('',views.store,name='store'),
    path('category/<slug:category_slug>',views.store,name='products_by_category'),
    path('cart/',views.cart,name='cart'),
    path('category/<slug:category_slug>/<slug:product_slug>',views.product_detail,name='product_details'),
    path('add_cart/<int:product_id>/',views.add_cart,name ='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>',views.remove_cart,name ='remove_cart'),
    path('remove_cart_item/<int:product_id>/',views.remove_cart_item,name ='remove_cart_item'),
    path('search/',views.search,name='search'),
]