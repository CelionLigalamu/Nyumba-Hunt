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
    phone_number = models.CharField(max_length=20)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.house.title}"

