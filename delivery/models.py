from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

class Product(models.Model):
    CATEGORIES = (
        ('Produce', 'Produce'),
        ('Dairy and Eggs', 'Dairy and Eggs'),
        ('Meat and Seafood', 'Meat and Seafood'),
        ('Bakery', 'Bakery'),
        ('Pantry Staples', 'Pantry Staples'),
        ('Frozen Foods', 'Frozen Foods'),
        ('Beverages', 'Beverages'),
        ('Snacks', 'Snacks'),
        ('Canned and Jarred Goods', 'Canned and Jarred Goods'),
        ('Condiments', 'Condiments'),
        ('Spices and Seasonings', 'Spices and Seasonings'),
        ('Deli and Prepared Foods', 'Deli and Prepared Foods'),
        ('Household and Cleaning Supplies', 'Household and Cleaning Supplies'),
        ('Baby and Child Care', 'Baby and Child Care'),
        ('Health and Wellness', 'Health and Wellness'),
        ('Pet Supplies', 'Pet Supplies'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    is_available = models.BooleanField(default=True)

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image_url = models.TextField()

    def __str__(self):
        return f"{self.product_name} - {self.user.username}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
