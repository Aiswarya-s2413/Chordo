from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import ProductOffer, ProductVariant,CategoryOffer, Product, ProductVariant
from django.db.models import F

@receiver(post_save, sender=ProductOffer)
def apply_offer_to_variants(sender, instance, **kwargs):
    print(f"Applying offer: {instance.name} to product variants")
    product = instance.product
    variants = ProductVariant.objects.filter(product=product)

    for variant in variants:
        if instance.discount_percentage:
            discount = (variant.price * instance.discount_percentage) / 100
            variant.discounted_price = variant.price - discount
        elif instance.discount_amount:
            discount = instance.discount_amount
            variant.discounted_price = max(0, variant.price - discount)  # Ensure no negative prices
        else:
            # No discount
            variant.discounted_price = variant.price
        variant.save()


@receiver(pre_delete, sender=ProductOffer)
def remove_offer_from_variants(sender, instance, **kwargs):
    
    product = instance.product
    variants = ProductVariant.objects.filter(product=product)

    for variant in variants:
        variant.discounted_price = variant.price  # Revert to original price
        variant.save()


@receiver(post_save, sender=CategoryOffer)
def apply_category_offer(sender, instance, **kwargs):
    category = instance.category
    products = Product.objects.filter(category=category, is_deleted=False)

    for product in products:
        product_variants = product.variants.filter(is_deleted=False)

        if instance.discount_percentage:
            discount_factor = (100 - instance.discount_percentage) / 100
            for variant in product_variants:
                variant.discounted_price = variant.price * discount_factor
                variant.save()
        elif instance.discount_amount:
            for variant in product_variants:
                variant.discounted_price = max(0, variant.price - instance.discount_amount)
                variant.save()


@receiver(pre_delete, sender=CategoryOffer)
def remove_category_offer(sender, instance, **kwargs):
    category = instance.category
    products = Product.objects.filter(category=category, is_deleted=False)

    for product in products:
        product_variants = product.variants.filter(is_deleted=False)
        for variant in product_variants:
            variant.discounted_price = variant.price  # Revert to original price
            variant.save()