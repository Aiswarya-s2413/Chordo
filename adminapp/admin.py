
from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from .models import Offer, ProductOffer, CategoryOffer

# Get all models in this app
app = apps.get_app_config('adminapp')

for model_name, model in app.models.items():
    try:
        admin.site.register(model)   #registering all models
    except AlreadyRegistered:
        pass



# @admin.register(ProductOffer)      #This is done to make offer management in django admin more easier
# class ProductOfferAdmin(admin.ModelAdmin):
#     list_display = ('name', 'product', 'discount_percentage', 'discount_amount', 'start_date', 'end_date', 'is_active')
#     list_filter = ('is_active', 'start_date', 'end_date')
#     search_fields = ('name', 'product__name')

# @admin.register(CategoryOffer)
# class CategoryOfferAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category', 'discount_percentage', 'discount_amount', 'start_date', 'end_date', 'is_active')
#     list_filter = ('is_active', 'start_date', 'end_date')
#     search_fields = ('name', 'category__name')
