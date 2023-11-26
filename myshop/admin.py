from django.contrib import admin

# Register your models here.
from .models import Category,Product,CartItem,Cart,Variation



class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product','cart','quantity','is_active')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category')
    prepopulated_fields = {'slug': ('name',)}


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active')
    list_editable = ('is_active',)


admin.site.register(Category,CategoryAdmin)

admin.site.register(Product,ProductAdmin)

admin.site.register(Cart)
admin.site.register(CartItem,CartItemAdmin)
admin.site.register(Variation,VariationAdmin)


