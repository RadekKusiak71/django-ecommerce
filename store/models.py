from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street = models.CharField(max_length=100, null=True, blank=True)
    house_number = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    discount_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Customer#{self.id}, {self.user.first_name} {self.user.last_name}'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products', null=True, blank=True)
    quantity = models.PositiveIntegerField()
    discount = models.PositiveIntegerField(null=True, blank=True)
    sales_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        if not self.discount:
            return f'{self.title} - {self.price}$ discount '
        return f'{self.title} - {self.price * (self.discount / 100)}'


class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)
    total = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Cart#{self.id} for customer#{self.customer.id}, total: {self.total}$'


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.product.title} / {self.quantity}'


class Order(models.Model):
    STATUS_CHOICES = (
        ('p', 'Pending'),
        ('c', 'Cancelled'),
        ('d', 'Declined'),
        ('ap', 'Awaiting Pickup'),
        ('as', 'Awaiting Shipment'),
        ('cp', 'Completed'),
        ('pr', 'Preparing'),
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    # Shipping data
    shipping_address = models.TextField()
    shipping_street = models.CharField(max_length=100)
    shipping_house_number = models.CharField(
        max_length=100, null=True, blank=True)
    shipping_zip_code = models.CharField(max_length=100)
    shipping_city = models.CharField(max_length=100)
    shipping_country = CountryField()
    shipping_status = models.CharField(max_length=3, choices=STATUS_CHOICES)

    def __str__(self):
        return f'Order#{self.id} for customer#{self.customer.id}, total: {self.total}$'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product.title} in Order#{self.order.id}, quantity: {self.quantity}'
