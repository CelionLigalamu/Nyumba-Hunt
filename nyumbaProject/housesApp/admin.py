# Register your models here.
from django.contrib import admin
from .models import House, Booking, Payment

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'status')
    list_filter = ('status', 'location')
    search_fields = ('title', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'house', 'phone_number', 'booking_date')
    search_fields = ('user__username', 'house__title')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking__user__username', 'phone_number', 'mpesa_receipt_number')
    readonly_fields = ('created_at', 'updated_at', 'checkout_request_id')

