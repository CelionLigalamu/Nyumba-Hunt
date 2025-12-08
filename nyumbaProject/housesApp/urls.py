from django.urls import path
from . import views
from .views import register_user
app_name='housesApp'

urlpatterns = [
    path('', views.home, name='home'),
    path('house/<int:pk>/', views.house_detail, name='house_detail'),  # detail page
    path('book/<int:pk>/', views.book_house, name='book_house'),      # booking page
    path('register/', register_user, name='register'),
    path('dashboard/', views.landlord_dashboard, name='dashboard'),
]




