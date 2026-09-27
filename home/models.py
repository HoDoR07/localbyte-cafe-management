from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to="menu/", blank=True, null=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CafeTable(models.Model):

    TABLE_STATUS = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("reserved", "Reserved"),
    ]


    table_number = models.IntegerField()
    capacity = models.IntegerField()
    table_status = models.CharField(max_length=20,choices=TABLE_STATUS, default="available")

    def __str__(self):
        return f"Table {self.table_number}"


class Reservation(models.Model):
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_guests = models.IntegerField()
    table = models.ForeignKey(CafeTable, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)

    TOKEN_PAYMENT_STATUS = [
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("failed", "Failed"),
    ]

    token_payment_status = models.CharField(max_length=20, choices=TOKEN_PAYMENT_STATUS, default="pending")

    RESERVATION_STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    status = models.CharField(max_length=20, choices=RESERVATION_STATUS, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "table",
                    "reservation_date",
                    "reservation_time"
                ],
                name="unique_table_reservation"
            )
        ]


    def __str__(self):
        return f"{self.customer.username} - Table {self.table.table_number}"


class Invoice(models.Model):

    invoice_number = models.CharField(max_length=50, unique=True)
    reservation = models.OneToOneField(Reservation, on_delete = models.CASCADE)
    customer = models.ForeignKey(User, on_delete = models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, default="UPI")
    payment_status = models.CharField(max_length= 20, default="paid")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number


class Cart(models.Model):

    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.customer:
            return f"Cart - {self.customer.username}"

        return f"Guest Cart - {self.session_key}"


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} - {self.quantity}" 


class Order(models.Model):

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(CafeTable, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    ORDER_STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    status = models.CharField(max_length=20, choices=ORDER_STATUS, default="pending")

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"



class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item} - {self.quantity}"


class OrderInvoice(models.Model):
    
    invoice_number = models.CharField(max_length=50, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, default="UPI")
    payment_status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_number}"



class Payment(models.Model):

    PAYMENT_METHODS = [
        ("upi", "UPI"),
        ("card", "Credit / Debit Card"),
        ("cash", "Cash"), 
    ]

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__ (self):
        return f"Payment for Order #{self.order.id}"


    

class InventoryItem(models.Model):

    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class StockTransaction(models.Model):

    TRANSACTION_TYPE = [
        ("purchase", "Purchase"),
        ("issue", "Stock Issue"),
        ("consumption", "Consumption"),
        ("adjustment", "Adjustment"),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inventory_item.name} - {self.transaction_type}"



class KitchenStock(models.Model):

    inventory_item = models.OneToOneField(InventoryItem, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.inventory_item.name} - Kitchen Stock"




class CafeSetting(models.Model):

    cafe_name = models.CharField(
        max_length=100,
        default="Local:Byte"
    )

    tagline = models.CharField(
        max_length=200,
        default="Sip. Script. Savor."
    )

    phone = models.CharField(
        max_length=20,
        default="0000000000"
    )

    email = models.EmailField(
        default="temp@example.com"
    )

    address = models.CharField(
        max_length=200,
        default="Hazaribagh, Jharkhand"
    )

    instagram = models.URLField(blank=True)

    facebook = models.URLField(blank=True)

    whatsapp = models.CharField(
        max_length=20,
        blank=True
    )

    opening_time = models.TimeField(
        default="09:00"
    )

    closing_time = models.TimeField(
        default="22:00"
    )

    about = models.TextField(
        default="Local:Byte Cafe"
    )

    special_offer = models.BooleanField(default=False)
    
    special_offer_text = models.CharField(max_length=200, blank=True)

    gst_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5.00
    )


    def __str__(self):
        return self.cafe_name



class ContactMessage(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
