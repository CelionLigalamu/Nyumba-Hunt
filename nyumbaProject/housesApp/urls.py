from django.urls import path
from . import views
from .views import register_user, login_user, initiate_payment, payment_callback
app_name='housesApp'

urlpatterns = [
    path('', views.home, name='home'),
    path('house/<int:pk>/', views.house_detail, name='house_detail'),
    path('book/<int:pk>/', views.book_house, name='book_house'),
    path('login/', login_user, name='login'),
    path('register/', register_user, name='register'),
    path('dashboard/', views.landlord_dashboard, name='dashboard'),
    path('payment/<int:booking_id>/', initiate_payment, name='initiate_payment'),
    path('payment/callback/', payment_callback, name='payment_callback'),
]




