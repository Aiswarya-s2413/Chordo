from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from adminapp.models import *

@receiver(post_save, sender=settings.AUTH_USER_MODEL)  #create wallet automatically when user is created
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=OrderItem)
def check_order_cancellation(sender, instance, **kwargs):
    if instance.status == 'cancelled' and instance.order.payment_method == 'razorPay':
        process_refund(instance)
    elif instance.status == 'returned':
        process_refund(instance)

def process_refund(order_item):
    order = order_item.order
    
    total_items = sum(item.quantity for item in order.order_items.all())
    shared_amount = (order.total_price-order.discount_amount) / total_items
    price = order_item.price-shared_amount

    refund_amount = price * order_item.quantity
    wallet, created = Wallet.objects.get_or_create(user=order_item.order.user)
 
    wallet.balance += refund_amount
    wallet.save()
    print(f"Wallet balance after update: {wallet.balance}")