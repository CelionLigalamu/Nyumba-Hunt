# Register your models here.
from django.contrib import admin
from .models import House, Booking

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'status')
    list_filter = ('status', 'location')
    search_fields = ('title', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'house', 'phone_number', 'booking_date')
    search_fields = ('user__username', 'house__title')

