# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class House(models.Model):
    STATUS_VACANT = 'vacant'
    STATUS_OCCUPIED = 'occupied'
    STATUS_CHOICES = [
        (STATUS_VACANT, 'Vacant'),
        (STATUS_OCCUPIED, 'Occupied'),
    ]

    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='house_images/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_VACANT)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='houses', null=True, blank=True)

    def __str__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='bookings')
    phone_number = models.CharField(max_length=10)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.house.title}"


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20)
    checkout_request_id = models.CharField(max_length=255, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    mpesa_receipt_number = models.CharField(max_length=100, null=True, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status} - Ksh {self.amount}"

    class Meta:
        ordering = ['-created_at']

