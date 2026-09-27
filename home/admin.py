from django.contrib import admin
from .models import (MenuItem, Category, CafeTable, Reservation, Invoice, Cart, 
                     CartItem, Order, OrderItem, OrderInvoice, InventoryItem, 
                     StockTransaction, KitchenStock, CafeSetting, ContactMessage, Payment)



# Register your models here.

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(CafeTable)
admin.site.register(Reservation)
admin.site.register(Invoice)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderInvoice)
admin.site.register(InventoryItem)
admin.site.register(StockTransaction)
admin.site.register(KitchenStock)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "phone_number",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone_number",
    )

    ordering = (
        "-created_at",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "amount",
        "payment_method",
        "payment_status",
        "transaction_id",
        "created_at",
    )

    list_filter = (
        "payment_method",
        "payment_status",
    )

    search_fields = (
        "order__id",
        "transaction_id",
    )

    ordering = (
        "-created_at",
    )


@admin.register(CafeSetting)
class CafeSettingAdmin(admin.ModelAdmin):

    fieldsets = (

        (
            "Cafe Information",
            {
                "fields": (
                    "cafe_name",
                    "tagline",
                    "about",
                )
            }
        ),

        (
            "Contact Information",
            {
                "fields": (
                    "phone",
                    "email",
                    "address",
                )
            }
        ),

        (
            "Social Media",
            {
                "fields": (
                    "instagram",
                    "facebook",
                    "whatsapp",
                )
            }
        ),

        (
            "Opening Hours",
            {
                "fields": (
                    "opening_time",
                    "closing_time",
                )
            }
        ),

        (
            "Business Settings",
            {
                "fields": (
                    "gst_rate",
                    "special_offer",
                    "special_offer_text",
                )
            }
        ),

    )

    def has_add_permission(self, request):

        if CafeSetting.objects.exists():
            return False

        return True