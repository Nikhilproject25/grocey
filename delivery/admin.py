from django.contrib import admin
from .models import Product, CartItem, Order, OrderItem, Feedback


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'category', 'description')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_name', 'price', 'image_url', 'quantity')
    list_filter = ('user',)
    search_fields = ('user__username', 'product_name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at', 'total_price']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)

# Register the Product model with the custom admin options
admin.site.register(Product, ProductAdmin)

admin.site.register(Feedback)

