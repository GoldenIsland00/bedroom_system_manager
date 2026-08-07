from django.urls import path
from . import views

app_name = 'cafeteria'

urlpatterns = [
    path('menu/', views.weekly_menu, name='menu'),
    path('order/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('transactions/', views.transactions, name='transactions'),
    path('admin/menu/', views.admin_menu_manage, name='admin_menu'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
]
