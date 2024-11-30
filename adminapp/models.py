from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.conf import settings
import os
from decimal import Decimal
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Avg


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self,username,email,password=None,**extra_fields):
        if not email:
            raise ValueError('The Email field is necessary')
        if not username:
            raise ValueError('The Username field is necessary')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password) #Hash the password
        user.save(using=self._db) #Save the user to the database
        return user
    def create_superuser(self,username,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff' , True)
        extra_fields.setdefault('is_superuser' , True)

        return self.create_user(username,email,password,**extra_fields)
    
class CustomUser(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=150,unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    

    objects = CustomUserManager() #To use the custom user manager

    USERNAME_FIELD = 'email' #for authentication
    REQUIRED_FIELDS = ['username']    #required fields

    def __str__(self):
        return self.email #Return email when user instance is printed
    




# ===================== Base Model ===================== #
class BaseModel(models.Model):
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# ===================== Category Model ===================== #
class Category(BaseModel):
    name = models.CharField(max_length=100,unique=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete field

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.is_deleted = True  # Set as deleted instead of removing
        self.save()

    class Meta:
        verbose_name_plural = "Categories"



#  Product Model  #
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    index = models.PositiveIntegerField(editable=False, null=True)
    is_featured = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Soft delete field

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True  
        self.save()
    
# Product Variant Model
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    color = models.CharField(max_length=50, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    popularity = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {self.color or 'Variant'}"
    
    def get_display_price(self):
        return self.discounted_price or self.price
    
    def save(self, *args, **kwargs):
        if self.discounted_price is None:
            self.discounted_price = self.price  # Default to original price if no discount applied
        super().save(*args, **kwargs)
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        return reviews.aggregate(Avg('rating'))['rating__avg'] or 0  

    def delete(self, *args, **kwargs):
        self.is_deleted = True  
        self.save()


#  Image Model  #
class Image(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
    image = models.ImageField(upload_to='product_images/', max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Image {self.id} for {self.variant.product.name}"
    
    @property
    def url(self):
        return self.image.url
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True  # Set as deleted instead of removing
        self.save()


# Review Model#
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='reviews',null=False)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.variant.product.name}: {self.rating} stars by {self.user.username}"

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=15,unique=True, blank=True, null=True, validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.email = self.user.email
        super().save(*args, **kwargs)  

    def __str__(self):
        return self.user.username
    
class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.address_line1}, {self.city}, {self.pincode}, {self.country}'
    
class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='cart')
    created_at=models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity=models.PositiveBigIntegerField(default=1)

    def get_total_price(self):
        return self.quantity*self.variant.get_display_price()
    
class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name="wishlist")
    created_at = models.DateTimeField(auto_now_add=True)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    variant= models.ForeignKey(ProductVariant, on_delete=models.CASCADE,related_name="wishlist_items")

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cashOnDelivery', 'Cash on Delivery'),
        ('razorPay', 'RazorPay'),
        ('wallet', 'Wallet'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField()
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, default="")
    is_paid = models.BooleanField(default=False)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cashOnDelivery'
    )
    delivery_charge = models.DecimalField(max_digits=10,decimal_places=2,default=100.0)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'
    

class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('order_recieved','Order Recieved'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned')
    ]
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="order_items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveBigIntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cancellation_reason = models.TextField(null=True, blank=True)
    return_reason = models.TextField(null=True, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    request_type = models.CharField(
        max_length=20,
        choices=[('cancel', 'Cancel'), ('return', 'Return')],
        null=True,
        blank=True,
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='nil',
    )
    request_date = models.DateTimeField(null=True, blank=True)

    def get_total_price(self):
        return self.quantity * self.variant.get_display_price()
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type=models.CharField(max_length=10,choices=[('fixed','Fixed'),('percentage','Percentage')])
    discount_value=models.DecimalField(max_digits=10, decimal_places=2)
    max_total_use=models.IntegerField(null=True,blank=True)
    max_use_per_user=models.IntegerField(null=True,blank=True)
    expiry_date=models.DateTimeField()
    min_order_amount=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)

    def __str__(self):
        return self.code
    
class UserCoupon(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE)
    use_count = models.IntegerField(default=0)

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet - Balance: {self.balance}"
    
class Offer(models.Model):
    name = models.CharField(max_length=100)  
    description = models.TextField(null=True, blank=True)  
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateTimeField()  
    end_date = models.DateTimeField() 
    is_active = models.BooleanField(default=True)  

class ProductOffer(Offer):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

class CategoryOffer(Offer):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

