from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/shop-setup/', views.shop_setup, name='shop_setup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('sell/', views.sell, name='sell'),
    path('customers/', views.customers, name='customers'),
    path('report/', views.report, name='report'),
]
