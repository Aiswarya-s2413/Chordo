from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import login ,logout ,authenticate
import re
from .otp_validate import *
from adminapp.models import *
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from .forms import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import transaction
from adminapp.constants import SORT_OPTIONS
from math import floor
import time
import razorpay
from django.http import JsonResponse
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.timezone import now
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.db.models import Q, Count, F

@never_cache
def userSignup(request):
    if request.user.is_authenticated:
            return redirect('userHome')
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password1')
        password2=request.POST.get('password2')

        User=get_user_model() #to get the user model currently being used

        if not username or not email or not password or not password2:
            messages.warning(request,'All fields are compulsory')
            return redirect('userSignup')

        if not re.match(r'^[a-zA-Z]+$', username):
            messages.warning(request,'Username must contain only alphabets')
            return redirect('userSignup')
        
        
        
        if not re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.warning(request,'Enter a valid email id')
        
        if len(password)<8:
            messages.warning(request,'Password must be greater than 8 characters')
            return redirect('userSignup')
        
        if password!=password2:
            messages.warning(request,'Passwords do not match')
            return redirect('userSignup')

        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            if not existing_user.is_active:
                otp = generate_otp() 
                request.session['otp'] = otp  
                request.session['email'] = email  
                request.session['otp_time'] = time.time()  

                send_otp(email, otp)

                return redirect('userOtp')

            else:
                messages.warning(request, 'Email already exists. Please login.')
                return redirect('userLogin')
        
        if User.objects.filter(email=email).exists():
            messages.warning(request,'Email already exists')
            return redirect('userSignup')

        user=User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
            )

        
        otp = generate_otp() 
        print(otp) 
        request.session['otp'] = otp  
        request.session['email'] = email  
        request.session['otp_time'] = time.time()  

        
        send_otp(email, otp)

        
        return redirect('userOtp')
    return render(request,'usersignup.html')
 
 #To validate OTP against OTP stored in session
@never_cache
def userOtp(request):
    if request.user.is_authenticated:
            return redirect('userHome')
    otp_expiry = 60  

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        otp_time = request.session.get('otp_time')
        email = request.session.get('email')

        if not stored_otp or not otp_time:
            return render(request, 'userotp.html', {'error': 'OTP has expired. Please request a new one.'})

        current_time = time.time()

        # Check if OTP is expired
        if current_time - otp_time > otp_expiry:
            return render(request, 'userotp.html', {'error': 'OTP has expired. Please request a new one.'})

        # Validate the OTP
        if str(otp_entered) == str(stored_otp):
            User = get_user_model()
            user = User.objects.get(email=email)
            user.is_active = True  
            user.save()

            messages.success(request, 'OTP verified successfully! You can now log in.')

            
            del request.session['otp']
            del request.session['email']
            del request.session['otp_time']
            return redirect('userLogin')
        else:
            return render(request, 'userotp.html', {'error': 'Invalid OTP'})

    else: 
        otp_time = request.session.get('otp_time')

        if otp_time:
            current_time = time.time()
            time_passed = current_time - otp_time
            time_left = int(otp_expiry - time_passed)

            if time_left < 0:
                time_left = 0  # If time has passed, set time left to 0
        else:
            time_left = otp_expiry  # Default to full time if no OTP time is found

        
        return render(request, 'userotp.html', {'time_left': time_left})
                                            

@never_cache
def resend_otp(request):
    if request.user.is_authenticated:
            return redirect('userHome') 
    if request.method == 'GET':  
        email = request.session.get('email')

        if not email:
            return redirect('userSignup') 
        
        # Generate a new OTP
        new_otp = generate_otp()
    
        request.session['otp'] = new_otp 
        request.session['otp_time'] = time.time() 

        # Send the new OTP to the user's email
        send_otp(email, new_otp)
        
        return redirect('userOtp')  

    return redirect('userOtp') 


@never_cache
def userLogin(request):
    if request.user.is_authenticated:
            return redirect('userHome')
    if request.method == 'POST':
        email = request.POST.get('username')  # This is email input 
        password = request.POST.get('password')

        if not email and not password:
            messages.warning(request, 'Please enter your email and password')
            return redirect('userLogin')

        if not email:
            messages.warning(request, 'Please enter your email')
            return redirect('userLogin')

        if not password:
            messages.warning(request, 'Please enter your password')
            return redirect('userLogin')

        # Authenticate using the email and password
        user = authenticate(request, username=email, password=password)


        if user is not None:
            login(request, user)
            return redirect('userHome')  
        else:
            messages.warning(request, 'Invalid email or password')
            return redirect('userLogin')

    return render(request, 'userlogin.html')
    

def userLogout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('userLogin')

def userHome(request):
    latest_products=ProductVariant.objects.filter(is_deleted=False,product__category__is_deleted=False).order_by('-id')[:4]
    best_products=ProductVariant.objects.filter(is_deleted=False,product__category__is_deleted=False).order_by('quantity')[:4]

    for product in latest_products:    #for handling rating
        avg_rating = product.average_rating or 0
        full_stars = int(floor(avg_rating))
        product.full_stars = range(full_stars)
        product.half_star = (avg_rating - full_stars) >= 0.5
        product.empty_stars = range(5 - full_stars - int(product.half_star))

    for product in best_products:
        avg_rating = product.average_rating or 0
        full_stars = int(floor(avg_rating))
        product.full_stars = range(full_stars)
        product.half_star = (avg_rating - full_stars) >= 0.5
        product.empty_stars = range(5 - full_stars - int(product.half_star))

    wishlist_items = []
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(wishlist__user=request.user).values_list('variant_id', flat=True)
    context={
        'latest_products':latest_products,
        'best_products':best_products,
        'wishlist_items' :wishlist_items,
        'user': request.user,
    }
    return render(request,'userhome.html',context)

@never_cache
def forgetPassword(request):
    if request.user.is_authenticated:
            return redirect('userHome')
    error_message=None
    User=get_user_model()
    if request.method=='POST':
        email=request.POST.get('email')
       
        try: 
            user = User.objects.get(email=email)
            reset_otp=generate_otp() 
            request.session['otp_reset'] = reset_otp 
            request.session['email'] = email 
            request.session['otp_time'] = time.time() 
            send_otp(email,reset_otp) 
            return redirect('passwordOtp')
        except User.DoesNotExist:
            error_message='Account does not exist'
            
    return render(request,'forgetpassword.html',{'error_message':error_message})

@never_cache
def resetPassword(request):
    if request.user.is_authenticated:
            return redirect('userHome')
    User = get_user_model()
    
    if request.method == 'POST':
        
        new_password = request.POST.get('passwordnew')
        confirm_password = request.POST.get('passwordconfirm')
        email = request.session.get('email')

        
        if not new_password or not confirm_password:
            messages.warning(request, 'All fields are compulsory')
            return render(request, 'resetpassword.html')

       
        if new_password == confirm_password:
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password successfully reset. You can now log in.")
                return redirect('userLogin')
            except User.DoesNotExist:
                messages.error(request, "No account found for this email.")
                return redirect('forgetPassword')
        else:
            messages.error(request, "Passwords do not match")
            return render(request, 'resetpassword.html')  # Return to the form in case of error
    
    
    return render(request, 'resetpassword.html')

    
    


@never_cache
def passwordOtp(request):
    if request.user.is_authenticated:
            return redirect('userHome')
    otp_expiry = 60
    if request.method=='POST':
        otp_given = request.POST.get('otp_password')
        original_otp = request.session.get('otp_reset')
        otp_timestamp = request.session.get('otp_time')
        print(original_otp)
        print(otp_given)

        current_time = time.time()

        if not original_otp or not otp_timestamp:
            return render(request, 'passwordotp.html', {'error': 'OTP has expired. Please request a new one.'})
        
        
        if current_time - otp_timestamp > otp_expiry:
            return render(request,'passwordotp.html',{'error': 'OTP has expired. Please request a new one.'})        
        
        if original_otp and str(otp_given) == str(original_otp):
            return redirect('resetPassword')

        else:
            return render(request,'passwordotp.html',{'error': 'Invalid OTP'})
    else:
        otp_timestamp = request.session.get('otp_time')
        if otp_timestamp:
            current_time=time.time()
            otp_expiry=60
            time_passed = current_time - otp_timestamp
            time_left = int(otp_expiry - time_passed)
            if time_left < 0:
                time_left = 0
        else:
            time_left = 60  # Default to full time if no OTP time is found

        return render(request, 'passwordotp.html', {'time_left': time_left})
     

@never_cache
def resend_otp_password(request):
    if request.user.is_authenticated:
            return redirect('userHome')
    if request.method == 'GET':  
        email = request.session.get('email')

        if not email:
            return redirect('userSignup') 
        
        # Generate a new OTP
        new_otp_resend = generate_otp()
    
        request.session['otp'] = new_otp_resend
        request.session['otp_time'] = time.time() 

        # Send the new OTP to the user's email
        send_otp(email, new_otp_resend)
        
        return redirect('passwordOtp') 
    return redirect('passwordOtp')  


def userCategories(request):
    categories = Category.objects.filter(is_deleted=False)
    return render (request,'usercategories.html',{'categories':categories})

#Product list display
# def productList(request):
#     sort_key = request.GET.get('sort', 'new_arrivals')
#     order_by = SORT_OPTIONS.get(sort_key, '-id')  

#     product_list = ProductVariant.objects.filter(
#         is_active=True,
#         is_deleted=False,
#         product__category__is_deleted=False
#     ).prefetch_related('images').order_by(order_by)
    
#     paginator = Paginator(product_list, 12)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     return render(request, 'productlist.html', {
#         'page_obj': page_obj,
#         'sort_key': sort_key,  
#     })

def productList(request):
    sort_key = request.GET.get('sort', 'new_arrivals')
    order_by = SORT_OPTIONS.get(sort_key, '-id')  

    product_list = ProductVariant.objects.filter(
        is_active=True,
        is_deleted=False,
        product__category__is_deleted=False
    ).prefetch_related('images').order_by(order_by)
    product = request.POST.get('searchproduct')
    if product:
            product_list = ProductVariant.objects.filter(
                product__name__icontains=product,
                is_deleted=False,
                product__category__is_deleted=False
            ).prefetch_related('images').order_by(order_by)

    for product in product_list:
        avg_rating = product.average_rating or 0
        full_stars = int(floor(avg_rating))
        product.full_stars = range(full_stars)  # List of full stars
        product.half_star = (avg_rating - full_stars) >= 0.5  # Single half-star
        product.empty_stars = range(5 - full_stars - int(product.half_star)) 
    
    paginator = Paginator(product_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    wishlist_items = []
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(wishlist__user=request.user).values_list('variant_id', flat=True)
    
    return render(request, 'productlist.html', {
        'page_obj': page_obj,
        'sort_key': sort_key, 
        'user': request.user,
        'wishlist_items' :wishlist_items, 
    })


#Detailed product view
def productView(request, id): #id of the variant
    product = get_object_or_404(ProductVariant, id=id)
    product.popularity += 1  
    product.save()
    
    related_products = ProductVariant.objects.filter(
        product=product.product, #to get variants of the same product 
        is_deleted=False
    )

    
    images = Image.objects.filter(variant=product)
    

    

    reviews = product.reviews.select_related('user').order_by('-created_at')

    # Get applicable offers
    
    
    avg_rating = product.average_rating or 0
    full_stars = int(floor(avg_rating))
    half_star = (avg_rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - int(half_star)

    other_products = ProductVariant.objects.filter(product__category=product.product.category,is_deleted=False, product__is_deleted=False).exclude(id=product.id)[:4]
    

    context = {
        'product': product,  
        'images': images,    
        'related_products': related_products,  
        'other_products':other_products,
        'reviews': reviews,  
        'avg_rating': avg_rating,
        'star_range': range(1, 6),
        'full_stars': [0] * full_stars, 
        'half_star': half_star,
        'empty_stars': [0] * empty_stars, 
    }

    return render(request, 'productview.html', context)

def categoryList(request,id):# id of category
    category = get_object_or_404(Category,id=id)
    products = ProductVariant.objects.filter(product__category=category,is_deleted=False,product__is_deleted=False,product__category__is_deleted=False)
    for product in products:
        avg_rating = product.average_rating or 0
        full_stars = int(floor(avg_rating))
        product.full_stars = range(full_stars)
        product.half_star = (avg_rating - full_stars) >= 0.5
        product.empty_stars = range(5 - full_stars - int(product.half_star))

    wishlist_items = []
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(wishlist__user=request.user).values_list('variant_id', flat=True)

    return render (request,'categorylist.html',{'category': category, 'products': products, 'user': request.user,'wishlist_items' :wishlist_items,})

@login_required(login_url='userLogin')
def userProfile(request):
    user = request.user
    
    profile, created = Profile.objects.get_or_create(user=user)
    
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile=form.save()
            new_username=profile.name
            if CustomUser.objects.filter(username=new_username).exclude(pk=user.id).exists():
                form.add_error('name', 'This name is already taken. Please choose another.')
            else:
                user.username = new_username  
                user.save()  
                return redirect('userProfile')  
        else:
            print(form.errors)     
    else:
         form = ProfileForm(instance=profile, initial={'name': user.username})
    
    return render(request, 'userprofile.html', {
        'form': form,
        'username': user.username,
        'email': user.email,
    })

@login_required(login_url='userLogin')
def addAddress(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_primary:
                Address.objects.filter(user=request.user, is_primary=True).update(is_primary=False)

            address.save()
            next_page = request.POST.get('next')
            if next_page == 'checkout':
                return redirect('userCheckout')
            else:
                return redirect('addAddress')
    else:
        form = AddressForm()

    addresses = Address.objects.filter(user=request.user)

    context = {
        'form':form,
        'addresses':addresses
    }
    return render(request, 'addaddress.html',context)
@login_required(login_url='userLogin')
def editAddress(request,id):
    address = get_object_or_404(Address,id=id)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            
            if address.is_primary:
                Address.objects.filter(user=request.user,is_primary=True).update(is_primary=False)

            address.save()
            return redirect('addAddress')

    else:
        form = AddressForm(instance=address)

    context = {
        'form': form,
        'address': address
    }
    return render(request, 'editaddress.html', context)       
    
@login_required(login_url='userLogin')
def deleteAddress(request, id):
    address = get_object_or_404(Address,id=id)

    if request.method == 'POST':
        address.delete()
        return redirect('addAddress')
@login_required(login_url='userLogin')   
def changePassword(request):
    if request.method == 'POST':
        # print(request.POST)
        form = ChangePasswordForm(user=request.user,data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user) #to keep user login after password change
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('changePassword')
        else:
            print(form.errors)
            print('not valid')
            messages.error(request,'Some error occured')

    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'changepassword.html',{'form':form})

@login_required(login_url='userLogin')
def userCart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(
        cart=cart
    ).select_related('variant__product').prefetch_related('variant__images')

    # Fetch valid coupons
    coupons = Coupon.objects.filter(
        expiry_date__gt=now()
    ).exclude(
        usercoupon__user=request.user,
        usercoupon__use_count__gte=models.F('max_use_per_user')  
    )

    price_total = sum(item.get_total_price() for item in cart_items)
    discount = 0
    selected_coupon = request.session.get('selected_coupon')  # Use session instead of POST

    # Handle coupon removal
    if request.method == 'POST' and request.POST.get('remove_coupon'):
        selected_coupon = None
        messages.success(request, "Coupon removed successfully.")
        request.session.pop('selected_coupon', None)

    elif request.method == 'POST' and request.POST.get('coupon_code'):
        selected_coupon = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=selected_coupon)

            # Ensure coupon is valid
            if coupon.expiry_date <= now():
                messages.error(request, "Coupon has expired.")
            elif UserCoupon.objects.filter(
                user=request.user,
                coupon=coupon,
                use_count__gte=coupon.max_use_per_user  # Validate max_use_per_user
            ).exists():
                messages.error(request, f"You have already used the coupon '{coupon.code}' the maximum number of times.")
            elif coupon.min_order_amount and price_total < coupon.min_order_amount:
                messages.error(request, f"Minimum order amount to use this coupon is ₹{coupon.min_order_amount}.")
            else:
                # Apply discount
                if coupon.discount_type == 'fixed':
                    discount = coupon.discount_value
                elif coupon.discount_type == 'percentage':
                    discount = (price_total * coupon.discount_value) / 100

                # Create or get UserCoupon entry WITHOUT incrementing use count
                user_coupon, created = UserCoupon.objects.get_or_create(
                    user=request.user,
                    coupon=coupon,
                    defaults={'use_count': 0}
                )

                # Save the selected coupon in session
                request.session['selected_coupon'] = coupon.code
                messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
        
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")

    # Render the template with context
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'price_total': price_total,
        'discount': discount,
        'coupons': coupons,
        'selected_coupon': selected_coupon
    })


@login_required(login_url='userLogin')
def addToCart(request, id):
    product = get_object_or_404(ProductVariant, id=id)
    product.popularity += 1
    product.save()

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=product)

    if not created:
        if cart_item.quantity < 4 and cart_item.quantity < product.quantity:
            cart_item.quantity += 1
        else:
            return JsonResponse({
                'success': False,
                'message': f"You can only add up to {min(4, product.quantity)} of this item."
            })

    cart_item.save()

    return JsonResponse({
        'success': True,
        'message': 'Item added to cart successfully!'
    })

@login_required(login_url='userLogin')
def wishlist(request):
    wishlist,created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = WishlistItem.objects.filter(wishlist=wishlist).select_related('variant__product').prefetch_related('variant__images')
    
    return render(request,'wishlist.html',{'wishlist_items':wishlist_items})

@login_required(login_url='userLogin')
def addToWishlist(request, id):  # id of the product variant
    product = get_object_or_404(ProductVariant, id=id)
    product.popularity += 1
    product.save()

    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, variant=product)

    if not created:
        return JsonResponse({'success': False, 'message': 'This product is already in your wishlist.'})

    wishlist_item.save() #only newly created

    return JsonResponse({'success': True, 'message': 'Product added to your wishlist!'})

@login_required(login_url='userLogin')
def removeFromWishlist(request,id): #id of wishlistitem
    wishlist_item = get_object_or_404(WishlistItem,id=id)
    wishlist_item.delete()
    return redirect('wishlist')

@login_required(login_url='userLogin')
def removeFromCart(request,id): #id of the item
    cart_item = get_object_or_404(CartItem,id=id)
    cart_item.delete()
    return redirect('userCart')

@login_required(login_url='userLogin')
def updateCartItem(request, id): #id of the item
    cart_item = get_object_or_404(CartItem, id=id)
    product = cart_item.variant
    
    if request.method == 'POST':
        quantity_change = int(request.POST.get("quantity_change", 0))
        
        new_quantity = cart_item.quantity + quantity_change
        
        if new_quantity < 1:
            cart_item.delete()
        elif new_quantity > 4 or new_quantity > product.quantity:
            cart_item.quantity = min(4,product.quantity)
            cart_item.save()
            if new_quantity > product.quantity:
                messages.warning(request, f"Only {product.quantity} of this item is available.")
            else:
                messages.warning(request,"Maximum 4 items allowed.")
        else:
            cart_item.quantity = new_quantity
            cart_item.save() 

    return redirect('userCart')  

@login_required(login_url='userLogin')
def userCheckout(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    primary_address = addresses.filter(is_primary=True).first()

    cart_items = CartItem.objects.filter(cart__user=request.user).select_related('variant')
    total_price = sum(item.get_total_price() for item in cart_items)
    print(total_price)

    delivery_charge = Decimal(100.0)  # Fixed delivery charge

    discount = Decimal(request.session.get('discount', 0))
    total_with_delivery = total_price + delivery_charge - discount
    discount_price = round(total_with_delivery - discount,4)
    
    order_placed = False
    razorpay_order = None  # Initialize razorpay_order

    out_of_stock=[]
    for item in cart_items:
        if item.quantity>item.variant.quantity:
            out_of_stock.append(item)

    if out_of_stock:
        messages.warning(request,"Insufficient stock. Please update your cart.")
        return redirect('userCart')
    
    address_form = AddressForm()

    if request.method == 'POST':
        address_id = request.POST.get('shipping_address_id')
        payment_method = request.POST.get('paymentMethod')

        if not address_id or not payment_method:
            messages.error(request, "Please select a shipping address and a payment method.")
            return redirect('userCheckout')

        selected_address = get_object_or_404(Address, id=address_id, user=request.user)
        selected_coupon_code = request.session.get('selected_coupon')

        if payment_method == 'cashOnDelivery':
            if total_with_delivery>1000:
                messages.error(request,"COD only available for orders below Rs.1000.")
                return redirect('userCheckout')
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=f"{selected_address.address_line1},{selected_address.address_line2}, {selected_address.city}, {selected_address.state}, {selected_address.country}, {selected_address.pincode}",
                    total_price=Decimal(total_with_delivery),
                    discount_amount=discount_price,
                    delivery_charge=delivery_charge,
                    is_paid=False,
                    payment_method='cashOnDelivery'
                )
                if selected_coupon_code:
                    try:
                        coupon = Coupon.objects.get(code=selected_coupon_code)
                        
                        # Check coupon validity again before finalizing the order
                        if (coupon.expiry_date <= timezone.now() or 
                            UserCoupon.objects.filter(
                                user=request.user,
                                coupon=coupon,
                                use_count__gte=coupon.max_use_per_user
                            ).exists()):
                            # If coupon is invalid, remove it from session
                            request.session.pop('selected_coupon', None)
                        else:
                            # Increment coupon use count
                            user_coupon, created = UserCoupon.objects.get_or_create(
                                user=request.user,
                                coupon=coupon,
                                defaults={'use_count': 0}
                            )
                            user_coupon.use_count += 1
                            user_coupon.save()
                            
                            # Optionally, clear the coupon from session after use
                            request.session.pop('selected_coupon', None)
                    
                    except Coupon.DoesNotExist:
                        # Handle case where coupon might have been deleted
                        request.session.pop('selected_coupon', None)


                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        quantity=item.quantity,
                        price=item.variant.price,
                        status='order_recieved'
                    )

                    item.variant.quantity -= item.quantity
                    item.variant.save()

                cart_items.delete()
                order_placed = True

                request.session.pop('discount', None)

        elif payment_method == 'razorPay':
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

            try:
                razorpay_order = client.order.create({
                    'amount': int(total_with_delivery * 100),  # amount in paise
                    'currency': 'INR',
                    'payment_capture': '1',
                })

                order = Order.objects.create(
                    user=request.user,
                    shipping_address=f"{selected_address.address_line1}, {selected_address.address_line2}, {selected_address.city}, {selected_address.state}, {selected_address.country}, {selected_address.pincode}",
                    total_price=Decimal(total_with_delivery),
                    discount_amount=discount_price,
                    delivery_charge=delivery_charge,
                    razorpay_order_id=razorpay_order['id'],
                    is_paid=False,
                    payment_method='razorPay'
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        quantity=item.quantity,
                        price=item.variant.price,
                    )

                #     item.variant.quantity -= item.quantity
                #     item.variant.save()

                # cart_items.delete()
                

            except razorpay.errors.BadRequestError as e:
                messages.error(request, f"Error creating Razorpay order: {str(e)}")
                return redirect('userCheckout')
         
        elif payment_method == 'wallet':
            wallet = Wallet.objects.get(user=request.user)  
            if wallet.balance >= total_with_delivery:  
                with transaction.atomic():
                    wallet.balance -= total_with_delivery
                    wallet.save()

                    order = Order.objects.create(
                        user=request.user,
                        shipping_address=f"{selected_address.address_line1}, {selected_address.address_line2}, {selected_address.city}, {selected_address.state}, {selected_address.country}, {selected_address.pincode}",
                        total_price=Decimal(total_with_delivery),
                        discount_amount=discount_price,
                        delivery_charge=delivery_charge,
                        is_paid=True,  
                        payment_method='wallet'
                    )

                    if selected_coupon_code:
                        try:
                            coupon = Coupon.objects.get(code=selected_coupon_code)
                        
                        # Check coupon validity again before finalizing the order
                            if (coupon.expiry_date <= timezone.now() or 
                                UserCoupon.objects.filter(
                                    user=request.user,
                                    coupon=coupon,
                                    use_count__gte=coupon.max_use_per_user
                                ).exists()):
                            # If coupon is invalid, remove it from session
                                request.session.pop('selected_coupon', None)
                            else:
                            # Increment coupon use count
                                user_coupon, created = UserCoupon.objects.get_or_create(
                                    user=request.user,
                                    coupon=coupon,
                                    defaults={'use_count': 0}
                                )
                                user_coupon.use_count += 1
                                user_coupon.save()
                            
                            # Optionally, clear the coupon from session after use
                                request.session.pop('selected_coupon', None)
                    
                        except Coupon.DoesNotExist:
                        # Handle case where coupon might have been deleted
                            request.session.pop('selected_coupon', None)

                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            variant=item.variant,
                            quantity=item.quantity,
                            price=item.variant.price,
                            status='order_recieved'
                        )

                        item.variant.quantity -= item.quantity
                        item.variant.save()

                    cart_items.delete()
                    order_placed = True
                    request.session.pop('discount', None)

            else:
                messages.error(request, "Insufficient balance in your wallet.")
                return redirect('userCheckout')
            
    return render(request, 'usercheckout.html', {
        'profile': profile,
        'addresses': addresses,
        'primary_address': primary_address,
        'cart_items': cart_items,
        'total_price': total_price,
        'order_placed': order_placed,
        'address_form': address_form,
        'razorpay_order': razorpay_order,
        'discount_price' : discount_price,
        'total_with_delivery' : total_with_delivery,
        'razorpay_key': settings.RAZORPAY_KEY_ID  
    })



@csrf_exempt
def verifyPayment(request):
    if request.method == 'POST':
        check = request.POST
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related('variant')
        selected_coupon_code = request.session.get('selected_coupon')
        # Initialize Razorpay client 
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        # Generate the signature hash and verify 
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)
            
            
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order_item = OrderItem.objects.filter(order=order.id)
            order.is_paid = True
            order.save()
            if selected_coupon_code:
                    try:
                        coupon = Coupon.objects.get(code=selected_coupon_code)
                        
                        # Check coupon validity again before finalizing the order
                        if (coupon.expiry_date <= timezone.now() or 
                            UserCoupon.objects.filter(
                                user=request.user,
                                coupon=coupon,
                                use_count__gte=coupon.max_use_per_user
                            ).exists()):
                            # If coupon is invalid, remove it from session
                            request.session.pop('selected_coupon', None)
                        else:
                            # Increment coupon use count
                            user_coupon, created = UserCoupon.objects.get_or_create(
                                user=request.user,
                                coupon=coupon,
                                defaults={'use_count': 0}
                            )
                            user_coupon.use_count += 1
                            user_coupon.save()
                            
                            # Optionally, clear the coupon from session after use
                            request.session.pop('selected_coupon', None)
                    
                    except Coupon.DoesNotExist:
                        # Handle case where coupon might have been deleted
                        request.session.pop('selected_coupon', None)
            for item in order_item:
                item.status = 'order_recieved'
                item.save()
                item.variant.quantity -= item.quantity
                item.variant.save()
          
            cart_items.delete()
            request.session.pop('discount', None)
            

            return render(request,'verifypayment.html')

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('userCheckout')

def retryPayment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        messages.info(request, "This order has already been paid for.")
        return redirect('orderHistory')

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

    try:
        total_price_in_paise = int(float(order.total_price+order.delivery_charge) * 100)
        razorpay_order = client.order.create({
            'amount': total_price_in_paise,  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1',
        })

        order.razorpay_order_id = razorpay_order['id']
        order.save()

        pay_amount=order.total_price+order.delivery_charge

        
        return render(request, 'razorpaycheckout.html', {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order': razorpay_order,  
            'total_price': order.total_price,
            'delivery_charge':order.delivery_charge,
            'pay_amount':pay_amount  
        })

    except razorpay.errors.BadRequestError as e:
        messages.error(request, f"Error creating Razorpay order: {str(e)}")
        return redirect('orderHistory')


def handlePaymentFailure(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        messages.info(request, "This order has already been paid for.")
        return redirect('orderHistory')

    order_items = order.items.all()

    # Ensure all order items are in 'pending' status
    for item in order_items:
        item.status = 'pending'
        item.save()

    messages.warning(request, "Your payment failed. Please complete the payment for this order.")
    return redirect('orderHistory')

@csrf_exempt  
def paymentSuccess(request):
    if request.method == "POST":
        # Razorpay client setup
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        
        # Extract payment details
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            
            # Update the order
            order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
            order.is_paid = True
            order.save()

            # Show success message
            messages.success(request, "Payment was successful!")
            return redirect('orderHistory')  # Redirect to order history or another page

        except razorpay.errors.SignatureVerificationError as e:
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect('orderHistory')

    messages.error(request, "Invalid payment request.")
    return redirect('orderHistory')


@login_required(login_url='userLogin')
def trackOrder(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('order_items__variant')

    orders_with_filtered_items = []

    for order in orders:
        filtered_items = order.order_items.exclude(status__in=["cancelled", "returned"])
        
        if filtered_items.exists(): 
            orders_with_filtered_items.append({
                'order': order,
                'order_items': filtered_items
            })

    return render(request, 'trackorder.html', {'orders_with_filtered_items': orders_with_filtered_items})

@login_required(login_url='userLogin')
def orderHistory(request):
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'delivered':
        orders = OrderItem.objects.filter(order__user=request.user,status='delivered')
    elif status_filter == 'cancelled':
        orders = OrderItem.objects.filter(order__user=request.user,status='cancelled')
    elif status_filter == 'returned':
        orders = OrderItem.objects.filter(order__user=request.user,status='returned')
    else:
        orders = OrderItem.objects.filter(order__user=request.user).all().order_by('-id')
    return render(request,'orderhistory.html',{'orders':orders,'review_form': ReviewForm()})


@login_required(login_url='userLogin')
def cancelOrder(request, id): #id of item        
    order_item = get_object_or_404(OrderItem, id=id, order__user=request.user)
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '').strip()  
        
        if not cancellation_reason:
            messages.error(request, "Cancellation reason is required.")
            return redirect('trackOrder')

        if re.match(r'^[\s\W]+$', cancellation_reason):
            messages.error(request, "Cancellation reason cannot consist only of spaces or punctuation.")
            return redirect('trackOrder')

        if len(cancellation_reason) < 10:
            messages.error(request, "Cancellation reason must be at least 10 characters long.")
            return redirect('trackOrder')  

        if order_item.status not in ["delivered", "Cancelled"]:
            order_item.request_type = "cancel"
            order_item.approval_status = "pending"
            order_item.cancellation_reason = cancellation_reason
            order_item.request_date = timezone.now()
            order_item.save()

            messages.success(request, "Your cancellation request has been submitted for admin approval.")
        else:
            messages.warning(request, "This order cannot be canceled.")
    
    return redirect('trackOrder')


@login_required(login_url='userLogin')
def returnOrder(request, id): #id of item
    order_item = get_object_or_404(OrderItem, id=id, order__user=request.user)
    
    if request.method == 'POST':
        return_reason = request.POST.get('return_reason', '').strip()  
        
        if not return_reason:
            messages.error(request, "Return reason is required.")
            return redirect('orderHistory')

        if re.match(r'^[\s\W]+$', return_reason):
            messages.error(request, "Return reason cannot consist only of spaces or punctuation.")
            return redirect('orderHistory')

        if len(return_reason) < 10:
            messages.error(request, "Return reason must be at least 10 characters long.")
            return redirect('orderHistory')  

        if order_item.status == "delivered":
            order_item.request_type = "return"
            order_item.approval_status = "pending"
            order_item.return_reason = return_reason
            order_item.request_date = timezone.now()
            order_item.save()

            messages.success(request, "Your return request has been submitted for admin approval.")
        else:
            messages.warning(request, "This order cannot be returned.")
    
    return redirect('orderHistory')

@login_required(login_url='userLogin')
def addReview(request, id): #id of item
    order_item = get_object_or_404(OrderItem, id=id, order__user=request.user)
    product = order_item.variant
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.variant = product
            review.save()
            messages.success(request, 'Review added successfully.')
            return redirect('orderHistory')
    else:
        form = ReviewForm()

    return render(request, 'orderhistory.html', {'form': form, 'product': product})

# def browseProduct(request):
#     sort_key = request.GET.get('sort', 'new_arrivals')
#     order_by = SORT_OPTIONS.get(sort_key, '-id')
    
#     # For GET request or if the search query is empty
#     if request.method == 'GET' or not request.POST.get('searchproduct'):
#         product_list = ProductVariant.objects.filter(
#             is_active=True,
#             is_deleted=False,
#             product__category__is_deleted=False
#         ).prefetch_related('images').order_by(order_by)
#     else:  # For POST request with a search product
#         product = request.POST.get('searchproduct')
#         if product:
#             product_list = ProductVariant.objects.filter(
#                 product__name__icontains=product,
#                 is_deleted=False,
#                 product__category__is_deleted=False
#             ).prefetch_related('images').order_by(order_by)
#         else:
#             product_list = ProductVariant.objects.filter(
#                 is_active=True,
#                 is_deleted=False,
#                 product__category__is_deleted=False
#             ).prefetch_related('images').order_by(order_by)

#     paginator = Paginator(product_list, 12)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

    
#     return render(request, 'browseproduct.html', {'page_obj': page_obj, 'sort_key': sort_key})

@login_required(login_url='userLogin')
def myWallet(request):
    wallet = Wallet.objects.get(user=request.user)
    refunded_order_items = OrderItem.objects.filter(
        order__user=request.user,
        status__in=['cancelled', 'returned']
    ).filter(
        models.Q(status='cancelled', order__payment_method='razorPay') | 
        models.Q(status='returned')
    ).order_by('-placed_at')

    refunded_items = []
    for item in refunded_order_items:
        order = item.order

        total_items = sum(i.quantity for i in order.order_items.all())
        
        shared_amount = (order.total_price - order.discount_amount) / total_items
        adjusted_price = item.price - shared_amount

        # Calculate refund amount for the current item
        refund_amount = adjusted_price * item.quantity
        refunded_items.append({
            'variant': item.variant,
            'quantity': item.quantity,
            'status': item.get_status_display(),
            'refund_amount': refund_amount,
        })                                                                                
    return render(request, 'mywallet.html', {'wallet': wallet,'refunded_order_items':refunded_items})

@login_required(login_url='userLogin')
def addMoney(request):
    if request.method == "POST":
        amount = Decimal(request.POST.get("amount", "0"))

        if amount <= 0:
            messages.error(request, "Invalid amount.")
            return redirect("addMoney")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        try:
            razorpay_order = client.order.create({
                'amount': int(amount * 100),  
                'currency': 'INR',
                'payment_capture': '1',  
            })

            context = {
                "amount": amount,
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "callback_url": "/wallet/payment-success/",
            }
            return render(request, "addmoney.html", context)

        except razorpay.errors.RazorpayError as e:
            messages.error(request, f"Error initiating payment: {str(e)}")
            return redirect("addMoney")

    return render(request, "addmoney.html")

@csrf_exempt
def walletPaymentSuccess(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        amount = Decimal(request.POST.get("amount", "0"))

        if payment_id:
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += amount
            wallet.save()

            messages.success(request, f"₹{amount} successfully added to your wallet!")
        else:
            messages.error(request, "Payment failed. Please try again.")

    return redirect("myWallet")


@login_required(login_url='userLogin')
def downloadInvoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    total_amount = order.discount_amount + order.delivery_charge

    # Render the HTML template to a string
    html_content = render_to_string(
        'downloadinvoice.html', 
        {
            'order': order,
            'total_amount': total_amount, 
        }
    )

    # Create a response object for the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Generate the PDF from the HTML content
    pisa_status = pisa.CreatePDF(html_content, dest=response)

    # Handle PDF generation errors
    if pisa_status.err:
        return HttpResponse("An error occurred while generating the PDF", status=500)

    return response
