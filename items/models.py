import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from mongoengine import (
    Document, EmbeddedDocument, StringField, DecimalField, IntField,
    DateTimeField, ImageField, EmbeddedDocumentListField,
)


def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class Item(Document):
    CATEGORY_CHOICES = (
        'Signature Karahi & Handi',
        'Tandoori & Charcoal BBQ',
        'Royal Biryani & Rice',
        'Appetizers & Soups',
        'Fresh Clay Oven Breads',
        'Desserts & Beverages',
    )

    name = StringField(max_length=200, required=True)
    category = StringField(max_length=100, default='Signature Karahi & Handi', choices=CATEGORY_CHOICES)
    description = StringField(max_length=2000, required=False, default='')
    price = DecimalField(min_value=0, precision=2, required=True, default=0)
    quantity = IntField(min_value=0, required=True, default=0)

    # Special-deal support: a percentage knocked off the regular price.
    discount_percent = DecimalField(min_value=0, max_value=90, precision=2, required=False, default=0)

    image = ImageField(required=False)

    created_at = DateTimeField(default=get_utc_now)
    updated_at = DateTimeField(default=get_utc_now)

    meta = {
        'collection': 'items',
        'ordering': ['-created_at'],
        'indexes': ['category'],
    }

    def __str__(self):
        return self.name

    @property
    def is_on_sale(self):
        return bool(self.discount_percent and self.discount_percent > 0)

    @property
    def discounted_price(self):
        if not self.is_on_sale:
            return self.price
        price = Decimal(str(self.price))
        pct = Decimal(str(self.discount_percent))
        discounted = price - (price * pct / Decimal(100))
        return discounted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def savings_amount(self):
        if not self.is_on_sale:
            return Decimal('0.00')
        return (Decimal(str(self.price)) - self.discounted_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def in_stock(self):
        return self.quantity > 0


class Profile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('employee', 'Employee'),
        ('customer', 'Customer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)


# ---------------------------------------------------------------------------
# Shopping cart
# ---------------------------------------------------------------------------

class CartItem(EmbeddedDocument):
    item_id = StringField(required=True)
    quantity = IntField(min_value=1, required=True, default=1)


class Cart(Document):
    user_id = IntField(required=True, unique=True)
    items = EmbeddedDocumentListField(CartItem)
    updated_at = DateTimeField(default=get_utc_now)

    meta = {
        'collection': 'carts',
        'indexes': ['user_id'],
    }

    def total_quantity(self):
        return sum(ci.quantity for ci in self.items)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

class OrderItem(EmbeddedDocument):
    item_id = StringField(required=True)
    name = StringField(required=True)
    unit_price = DecimalField(min_value=0, precision=2, required=True)
    quantity = IntField(min_value=1, required=True)

    @property
    def line_total(self):
        return (Decimal(str(self.unit_price)) * self.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Order(Document):
    STATUS_CHOICES = ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')

    user_id = IntField(required=True)
    username = StringField(required=True)

    items = EmbeddedDocumentListField(OrderItem)

    subtotal = DecimalField(min_value=0, precision=2, required=True, default=0)
    discount_total = DecimalField(min_value=0, precision=2, required=True, default=0)
    total = DecimalField(min_value=0, precision=2, required=True, default=0)

    shipping_name = StringField(max_length=200, required=True)
    shipping_address = StringField(max_length=500, required=True)
    shipping_city = StringField(max_length=200, required=True)
    shipping_phone = StringField(max_length=50, required=True)
    payment_method = StringField(max_length=50, required=True, default='cod')

    status = StringField(choices=STATUS_CHOICES, default='Pending')

    created_at = DateTimeField(default=get_utc_now)
    updated_at = DateTimeField(default=get_utc_now)

    meta = {
        'collection': 'orders',
        'ordering': ['-created_at'],
        'indexes': ['user_id', 'status'],
    }

    def __str__(self):
        return f"Order {self.id} ({self.username})"


# ---------------------------------------------------------------------------
# Table & Gazebo Reservations
# ---------------------------------------------------------------------------

class Reservation(Document):
    STATUS_CHOICES = ('Pending', 'Confirmed', 'Completed', 'Cancelled')
    TABLE_TYPE_CHOICES = (
        'Indoor Royal Hall',
        'Poolside VIP Gazebo',
        'Rooftop Star Gazing',
        'Private Dining Suite',
    )
    TIME_SLOT_CHOICES = (
        'Lunch (12:30 PM - 02:30 PM)',
        'Afternoon High Tea (04:00 PM - 06:00 PM)',
        'Sunset Dinner (07:30 PM - 09:30 PM)',
        'Midnight Feast (10:00 PM - 12:30 AM)',
    )

    user_id = IntField(required=True)
    username = StringField(required=True)

    guest_name = StringField(max_length=200, required=True)
    guest_email = StringField(max_length=200, required=True)
    guest_phone = StringField(max_length=50, required=True)
    guest_count = IntField(min_value=1, max_value=50, required=True, default=2)

    reservation_date = StringField(max_length=50, required=True)
    time_slot = StringField(choices=TIME_SLOT_CHOICES, required=True, default='Sunset Dinner (07:30 PM - 09:30 PM)')
    table_type = StringField(choices=TABLE_TYPE_CHOICES, required=True, default='Poolside VIP Gazebo')
    special_requests = StringField(max_length=1000, required=False, default='')

    status = StringField(choices=STATUS_CHOICES, default='Pending')

    created_at = DateTimeField(default=get_utc_now)
    updated_at = DateTimeField(default=get_utc_now)

    meta = {
        'collection': 'reservations',
        'ordering': ['-created_at'],
        'indexes': ['user_id', 'status', 'reservation_date'],
    }

    def __str__(self):
        return f"Reservation #{self.id} — {self.guest_name} ({self.table_type}, {self.reservation_date})"