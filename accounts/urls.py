from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('panel/students/', views.admin_students, name='admin_students'),
    path('panel/balance/<int:user_id>/', views.adjust_balance, name='adjust_balance'),
]
