from django.shortcuts import render,redirect
from .forms import *
from .models import *
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
import re 
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from openpyxl import Workbook
from django.utils.dateparse import parse_date
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.utils.timezone import now, timedelta, localtime
from django.http import JsonResponse
from django.db.models import Sum





@never_cache
def adminLogin(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('adminDashboard')
    User = get_user_model()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

       
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('adminDashboard')
            else:
                messages.error(request, 'You are not authorized to access this page.')
        else:
            messages.error(request, 'Invalid credentials')
    response = render(request, 'adminlogin.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate' 
    response['Pragma'] = 'no-cache'  
    response['Expires'] = '0'  
    return response

    # return render(request, 'adminlogin.html')

@login_required(login_url='adminLogin')
def adminLogout(request):
    if request.user.is_authenticated and request.user.is_superuser:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('adminLogin')


# @login_required(login_url='adminLogin')
def adminProduct(request):
    if request.user.is_superuser:
        filtered_variants = ProductVariant.objects.filter(is_deleted=False)
        products = Product.objects.filter(is_deleted=False, category__is_deleted=False) \
                  .prefetch_related(Prefetch('variants', queryset=filtered_variants)) \
                  .order_by('category_id') # Fetch only non-deleted products
        product_forms = []

        for product in products:
            form = ProductForm(instance=product)
            product_forms.append((product, form))  

        context = {
            'product_forms': product_forms,
        }
        return render(request, 'adminproduct.html', context)
    else:
        return redirect('adminLogin')

@login_required(login_url='adminLogin')
def addProduct(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            product_form = ProductForm(request.POST)

            if product_form.is_valid():
                product_form.save() 
                return redirect('adminProduct') 
        else:
            product_form = ProductForm() 

        context = {
            'product_form': product_form,
        }
        return render(request, 'addproduct.html', context)

    return redirect('adminLogin')

#add new variants
@login_required(login_url='adminLogin')
def addVariants(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_superuser:
        if request.method == 'POST':
            variant_formset = ProductVariantFormSet(request.POST, instance=product)
            image_formset = ProductImageFormSet(request.POST, request.FILES)

            if variant_formset.is_valid() and image_formset.is_valid():
                variants = variant_formset.save(commit=False)

                for variant in variants:
                    variant.product = product  
                    variant.save()

                    images = image_formset.save(commit=False)
                    for image in images:
                        image.variant = variant
                        image.save()

                return redirect('adminProduct')

        else:
            variant_formset = ProductVariantFormSet(queryset=ProductVariant.objects.none(), instance=product)
            image_formset = ProductImageFormSet(queryset=Image.objects.none())

        return render(request, 'addVariants.html', {
            'variant_formset': variant_formset,
            'image_formset': image_formset,
            'product': product,
        })

    return redirect('adminLogin')



# # Delete products
@login_required(login_url='adminLogin')
def deleteProduct(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            del_product = get_object_or_404(Product, id=id)
            
            del_product.delete()
            
            for variant in del_product.variants.all():
                variant.delete()  

        return redirect('adminProduct')
    
#delete variants
def deleteVariant(request,id): #variant id
    if request.user.is_superuser:
        if request.method == 'POST':
            del_variant = get_object_or_404(ProductVariant,id=id)
            del_variant.delete()
            return redirect('adminProduct')

# Search products
@login_required(login_url='adminLogin')
def searchProduct(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            product = request.POST.get('searchproduct')
            if product:
                products=Product.objects.filter(name__icontains=product)
            else:
                products=Product.objects.all()
            return render(request,'adminproduct.html',{'products':products})
    
# #Edit in product page
@login_required(login_url='adminLogin')
def editProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_superuser:
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product successfully edited')
                return redirect('adminProduct')
        else:
            form = ProductForm(instance=product)

        return render(request, 'adminproduct.html', {'form': form, 'product': product})


@login_required(login_url='adminLogin')
def editVariant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id, is_deleted=False)
    product = variant.product 
    variant_form = ProductVariantForm(request.POST or None, instance=variant)

    image_formset = ProductImageFormSet(
        request.POST or None,
        request.FILES or None,
        instance=variant,
        queryset=Image.objects.filter(is_deleted=False)
    )

    for form in image_formset:
        form.fields['id'].required = False
        form.fields['image'].required = False  
    if request.user.is_superuser:
        if request.method == 'POST':
            if variant_form.is_valid() and image_formset.is_valid():
                variant_form.save()
                image_formset.save()

                messages.success(request, 'Variant successfully edited')
                return redirect('adminProduct')  
            else:
                print("Variant form errors:", variant_form.errors)
                print("Image formset errors:", image_formset.errors)

        return render(request, 'editvariant.html', {
            'variant_form': variant_form,
            'image_formset': image_formset,
            'product': product,
            'variant': variant,
        })
    return redirect('adminLogin')

@login_required(login_url='adminLogin')
def adminCustomer(request):
    User = get_user_model()
    if request.user.is_superuser:
        users = User.objects.all().order_by('-date_joined')#retrieve from database 
        context = {
            'users':users #pass to template
        }   
        return render(request,'admincustomer.html',context)
    else:
        return redirect(adminLogin)

#Block customer
@login_required(login_url='adminLogin')
def blockUser(request,id):
    User = get_user_model()
    if request.user.is_superuser:
        if request.method == 'POST':
            user =get_object_or_404(User,id=id)
            if user.is_active:
                user.is_active = False
                user.save()
                messages.success(request,f'User {user.username} has been blocked.')
            else:
                messages.warning(request,'User is already blocked.')
            return redirect('adminCustomer')
    
#Unblock customer
@login_required(login_url='adminLogin')
def unblockUser(request,id):
    User = get_user_model()
    if request.user.is_superuser:
        if request.method == 'POST':
            user = get_object_or_404(User,id = id)
            if not user.is_active:
                user.is_active = True
                user.save()
                messages.success(request,f'User {user.username} has been unblocked.')
            else:
                messages.warning(request,f'User {user.username} has been unblocked.')
            return redirect('adminCustomer')
        
#Search customer
@login_required(login_url='adminLogin')
def searchUser(request):
    User = get_user_model()
    if request.user.is_superuser:
        if request.method == 'POST':
            user = request.POST.get('searchuser')
            if user:
                users=User.objects.filter(username__icontains=user).order_by('username')
            else:
                users=User.objects.all()
            return render(request,'admincustomer.html',{'users':users})


@login_required(login_url='adminLogin')
def adminDashboard(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    total_orders = Order.objects.count()
    total_sales = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_discounts = (
    Order.objects.annotate(
        discount=ExpressionWrapper(
            F('total_price') - F('discount_amount'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )
    .aggregate(Sum('discount'))['discount__sum'] or 0
)#ExpressionWrapper is used in Django to handle expressions that involve complex calculations or operations on model fields while ensuring that the resulting output has a specific type or format.

    net_sales = total_sales - total_discounts


    if start_date and end_date:
        custom_sales = Order.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).aggregate(
            total_sales=Sum('total_price'), total_discount=Sum('discount_amount')
        )
    else:
        custom_sales = {'total_sales': 0, 'total_discount': 0}

    today = localtime(now()).date()  # Current day
    start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
    start_of_month = today.replace(day=1)  # First day of the current month

    # Sales data for the current day
    daily_sales_data = Order.objects.filter(created_at__date=today)
    daily_sales = daily_sales_data.aggregate(Sum('total_price'))['total_price__sum'] or 0
    daily_discounts = (
                    daily_sales_data
                    .annotate(effective_discount=ExpressionWrapper(
                        F('total_price') - F('discount_amount'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    ))
                    .aggregate(total_effective_discount=Sum('effective_discount'))['total_effective_discount'] or 0
                )
    daily_net_sales = daily_sales - daily_discounts

    # Sales data for the current week
    weekly_sales_data = Order.objects.filter(created_at__date__range=[start_of_week, today])
    weekly_sales = weekly_sales_data.aggregate(Sum('total_price'))['total_price__sum'] or 0
    weekly_discounts = (
                    weekly_sales_data
                    .annotate(effective_discount=ExpressionWrapper(
                        F('total_price') - F('discount_amount'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    ))
                    .aggregate(total_effective_discount=Sum('effective_discount'))['total_effective_discount'] or 0
                )
    weekly_net_sales = weekly_sales - weekly_discounts

    # Sales data for the current month
    monthly_sales_data = Order.objects.filter(created_at__date__range=[start_of_month, today])
    monthly_sales = monthly_sales_data.aggregate(Sum('total_price'))['total_price__sum'] or 0
    monthly_discounts = (
                    monthly_sales_data
                    .annotate(effective_discount=ExpressionWrapper(
                        F('total_price') - F('discount_amount'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    ))
                    .aggregate(total_effective_discount=Sum('effective_discount'))['total_effective_discount'] or 0
                )
    monthly_net_sales = monthly_sales - monthly_discounts

    
    return render(request,'admindashboard.html',{
                        'custom_sales': custom_sales,
                        'total_sales': total_sales,
                        'total_discounts': total_discounts,
                        'net_sales': net_sales,
                        'total_orders':total_orders,
                        'daily_sales': daily_sales,
                        'daily_discounts': daily_discounts,
                        'daily_net_sales': daily_net_sales,
                        'weekly_sales': weekly_sales,
                        'weekly_discounts': weekly_discounts,
                        'weekly_net_sales': weekly_net_sales,
                        'monthly_sales': monthly_sales,
                        'monthly_discounts': monthly_discounts,
                        'monthly_net_sales': monthly_net_sales,
                        })

@login_required(login_url='adminLogin')
def topSellers(request):
    top_variants = ProductVariant.objects.filter(is_active=True, is_deleted=False).order_by('-popularity')[:10]
    top_products = (
        Product.objects.filter(is_active=True, is_deleted=False)
        .annotate(total_popularity=Sum('variants__popularity'))
        .order_by('-total_popularity')[:5]
    )
    top_categories = (
        Category.objects.filter(is_deleted=False)
        .annotate(total_popularity=Sum('product__variants__popularity'))
        .order_by('-total_popularity')[:3]
    )
    return render(request,'topsellers.html',{
                        'top_variants': top_variants,
                        'top_products': top_products,
                        'top_categories': top_categories,
                        })

@login_required(login_url='adminLogin')
def chart_data(request):
    filter_type = request.GET.get("filter", "monthly")

    labels = []
    sales = []
    orders = []

    if filter_type == "daily":
        today = now().date()
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        labels = [day.strftime("%Y-%m-%d") for day in last_7_days]
        sales = [
            Order.objects.filter(created_at__date=day).aggregate(total_sales=Sum("total_price"))["total_sales"] or 0
            for day in last_7_days
        ]
        orders = [Order.objects.filter(created_at__date=day).count() for day in last_7_days]

    elif filter_type == "monthly":
        current_month = now().month
        current_year = now().year
        labels = [
            (now() - timedelta(days=i * 30)).strftime("%B")
            for i in range(5, -1, -1)
        ]
        sales = [
            Order.objects.filter(
                created_at__month=(current_month - i) % 12 or 12,
                created_at__year=current_year - ((current_month - i) <= 0)
            ).aggregate(total_sales=Sum("total_price"))["total_sales"] or 0
            for i in range(5, -1, -1)
        ]
        orders = [
            Order.objects.filter(
                created_at__month=(current_month - i) % 12 or 12,
                created_at__year=current_year - ((current_month - i) <= 0)
            ).count()
            for i in range(5, -1, -1)
        ]

    elif filter_type == "yearly":
        current_year = now().year
        years = [current_year - i for i in range(3, -1, -1)]
        labels = [str(year) for year in years]
        sales = [
            Order.objects.filter(created_at__year=year).aggregate(total_sales=Sum("total_price"))["total_sales"] or 0
            for year in years
        ]
        orders = [Order.objects.filter(created_at__year=year).count() for year in years]

    data = {"labels": labels, "sales": sales, "orders": orders}
    return JsonResponse(data)

def downloadReport(request):
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return HttpResponse("Please provide start_date and end_date parameters.", status=400)

    start_date = parse_date(start_date) #Converts the date strings into Python date objects using parse_date.
    end_date = parse_date(end_date)
    if not start_date or not end_date:
        return HttpResponse("Invalid date format.", status=400)

    sales_data = Order.objects.filter(created_at__date__range=[start_date, end_date])

    total_sales = sales_data.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_discounts = (
                    sales_data
                    .annotate(effective_discount=ExpressionWrapper(
                        F('total_price') - F('discount_amount'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    ))
                    .aggregate(total_effective_discount=Sum('effective_discount'))['total_effective_discount'] or 0
                )
    net_sales = total_sales - total_discounts

    download_type = request.GET.get('download_type', 'excel')

    if download_type == 'excel':
        # Generate Excel report
        wb = Workbook()
        ws = wb.active
        ws.title = "Sales Report"

        # Add headers
        headers = ['Date', 'Order ID', 'Total Sales', 'Discount']
        ws.append(headers)

        # Add data to Excel
        for order in sales_data:
            ws.append([
                order.created_at.strftime('%Y-%m-%d'),
                order.id,
                float(order.total_price),
                float(order.discount_amount)
            ])

        # Prepare Excel response
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_{end_date}.xlsx"'
        wb.save(response)
        return response

    elif download_type == 'pdf':
        # Generate PDF report
        html_string = render_to_string('salesreport.html', {
            'sales_data': sales_data,
            'total_sales': total_sales,
            'total_discounts': total_discounts,
            'net_sales': net_sales,
            'start_date': start_date,
            'end_date': end_date,
        })

        # Create PDF from HTML
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_{end_date}.pdf"'

        # Generate the PDF with xhtml2pdf
        pisa_status = pisa.CreatePDF(html_string, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500) #internal error

        return response

    else:
        return HttpResponse("Invalid download type. Use 'excel' or 'pdf'.", status=400) # bad request


@login_required(login_url='adminLogin')
def adminCategory(request):
    if request.user.is_superuser:
        categories = Category.objects.all 
        return render(request,'admincategory.html',{'categories':categories})
    else:
        return redirect('adminLogin')
    
#search category
@login_required(login_url='adminLogin')
def searchCategory(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            category = request.POST.get('searchcategory')
            if category:
                categories=Category.objects.filter(name__icontains=category)
            else:
                categories = Category.objects.filter(is_deleted=False)
            return render(request,'admincategory.html',{'categories':categories})
            

#delete category
@login_required(login_url='adminLogin')
def deleteCategory(request,id):
    if request.user.is_superuser:
        if request.method == 'POST':
            category = Category.objects.get(id=id)
            category.is_active=False
            category.is_deleted=True
            category.save()

    return redirect('adminCategory')

@login_required(login_url='adminLogin')
def unblockCategory(request,id):
    if request.user.is_superuser:
        if request.method == 'POST':
            category = Category.objects.get(id=id)
            category.is_active=True
            category.is_deleted=False
            category.save()

    return redirect('adminCategory')

#add category
@login_required(login_url='adminLogin')
def addCategory(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            category_name = request.POST.get('name').strip()
            if not category_name or re.match(r'^[\W_]+$', category_name):
                messages.warning(request, 'Category name cannot consist only of spaces or symbols')
                return redirect('adminCategory')
            if Category.objects.filter(name__iexact=category_name).exists():
                messages.warning(request, 'Category with this name already exists')
                return redirect('adminCategory')
            elif category_name:
                Category.objects.create(name=category_name)
                messages.success(request, 'Category added successfully')
                return redirect('adminCategory')  
            else:
                messages.warning(request, 'Category name cannot be empty')
                return redirect('adminCategory')
        return HttpResponse(status=400)



#edit category
@login_required(login_url='adminLogin')
def editCategory(request, id):
    category = get_object_or_404(Category, id=id)
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST.get('name').strip()
            if not name or re.match(r'^[\W_]+$', name):
                messages.warning(request, 'Category name cannot consist only of spaces or symbols')
                return redirect('adminCategory')

            if Category.objects.filter(name__iexact=name).exclude(id=category.id).exists():
                messages.warning(request, 'Category with this name already exists')
                return redirect('adminCategory')
            
            category.name = name
            category.save()
            messages.success(request, 'Category updated successfully')
            return redirect('adminCategory')

        
@login_required(login_url='adminLogin')
def adminOrder(request):
    if request.user.is_superuser:
        orders = Order.objects.prefetch_related('order_items').all().order_by('-id')
        order_status_choices = OrderItem.STATUS_CHOICES
        selected_order = None

        if 'order_id' in request.GET:
            selected_order = get_object_or_404(Order,id=request.GET['order_id'])

        return render(request,'adminorder.html',{'orders':orders,'order_status_choices': order_status_choices, 'selected_order': selected_order})
    else:
        return redirect('adminLogin')
        

@login_required(login_url='adminLogin')
def admineditOrder(request,id): #id of order
    order = get_object_or_404(OrderItem,id=id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        order.status = new_status 
        order.save()

        messages.success(request,f"Order status updated")
        return redirect('adminOrder')

    return redirect('adminOrder')

@login_required(login_url='adminLogin')
def searchOrder(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            order = request.POST.get('searchorder')
            if order:
                orders=Order.objects.filter(order_items__product__name__icontains=order).distinct()
            else:
                orders = Order.objects.prefetch_related('order_items').all().order_by('id')
            return render(request,'adminorder.html',{'orders':orders})
        
@login_required(login_url='adminLogin')
def adminCoupon(request):
    if request.user.is_superuser:
        coupons = Coupon.objects.all().order_by('-id')
        return render(request,'admincoupon.html',{'coupons':coupons})

@login_required(login_url='adminLogin')
def addCoupon(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            coupon_form = CouponForm(request.POST)

            if coupon_form.is_valid():
                coupon_form.save()
                return redirect('adminCoupon')
        
        else:
            coupon_form = CouponForm()

        context = {
            'coupon_form': coupon_form
        }
        return render(request,'addcoupon.html',context)
    
    return redirect('adminLogin')

@login_required(login_url='adminLogin')
def editCoupon(request, coupon_id):
    coupon = get_object_or_404(Coupon,id=coupon_id)
    if request.user.is_superuser:
        if request.method == 'POST':
            form = CouponForm(request.POST, instance=coupon)
            if form.is_valid():
                form.save()
                messages.success(request, 'Coupon successfully edited')
                return redirect('adminCoupon')
        else:
            form = CouponForm(instance=coupon)
        return render(request, 'admincoupon.html', {'form': form, 'coupon': coupon})

@login_required(login_url='adminLogin')   
def deleteCoupon(request,coupon_id):
    if request.user.is_superuser:
        if request.method=='POST':
            del_coupon = Coupon.objects.get(id=coupon_id)
            del_coupon.delete()
            messages.success(request, 'Coupon removed successfully')

    return redirect('adminCoupon')

@login_required(login_url='adminLogin')  
def searchCoupon(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            coupon = request.POST.get('searchcoupon')
            if coupon:
                coupons=Coupon.objects.filter(code__icontains=coupon)
            else:
                coupons= Coupon.objects.all()
            return render(request,'admincoupon.html',{'coupons':coupons})

@login_required(login_url='adminLogin')        
def adminOffers(request):
    product_offers = ProductOffer.objects.all()
    category_offers = CategoryOffer.objects.all()
    return render(request, 'adminoffer.html', {
        'product_offers': product_offers,
        'category_offers': category_offers,
    })

@login_required(login_url='adminLogin')
def addProductOffer(request):
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminOffers')
    else:
        form = ProductOfferForm()
    return render(request, 'addoffer.html', {'form': form, 'type': 'Product Offer'})

@login_required(login_url='adminLogin')
def addCategoryOffer(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminOffers')
    else:
        form = CategoryOfferForm()
    return render(request, 'addoffer.html', {'form': form, 'type': 'Category Offer'})

@login_required(login_url='adminLogin')
def editOffer(request, offer_type, id):
    if offer_type == 'product':
        offer = get_object_or_404(ProductOffer, id=id)
        form_class = ProductOfferForm
    elif offer_type == 'category':
        offer = get_object_or_404(CategoryOffer, id=id)
        form_class = CategoryOfferForm
    else:
        return redirect('list_offers')
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('adminOffers')
        else:
            print(form.errors)
    else:
        form = form_class(instance=offer)
    return render(request, 'editoffer.html', {'form': form, 'type': f'{offer_type.capitalize()} Offer'})

@login_required(login_url='adminLogin')
def deleteOffer(request, offer_type, id):
    if offer_type == 'product':
        offer = get_object_or_404(ProductOffer, id=id)
    elif offer_type == 'category':
        offer = get_object_or_404(CategoryOffer, id=id)
    else:
        return redirect('adminOffers')
    
    offer.delete()
    return redirect('adminOffers')

@login_required(login_url='adminLogin')
def manageRequests(request):
    pending_requests = OrderItem.objects.filter(approval_status='pending')

    if request.method == 'POST':
        order_item_id = request.POST.get('order_item_id')
        action = request.POST.get('action')  # 'approve' or 'reject'
        order_item = get_object_or_404(OrderItem, id=order_item_id)

        if action == 'approve':
            order_item.approval_status = 'approved'
            if order_item.request_type == 'cancel':
                order_item.status = 'cancelled'
                variant = order_item.variant
                variant.quantity += order_item.quantity
                variant.save()
            elif order_item.request_type == 'return':
                order_item.status = 'returned'
                variant = order_item.variant
                variant.quantity += order_item.quantity
                variant.save()
            messages.success(request, f"Request approved for order item {order_item.id}.")
        elif action == 'reject':
            order_item.approval_status = 'rejected'
            messages.warning(request, f"Request rejected for order item {order_item.id}.")

        order_item.save()
        return redirect('manageRequests')

    return render(request, 'managerequests.html', {'pending_requests': pending_requests})



    
