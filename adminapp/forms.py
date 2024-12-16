from django import forms
from django.forms import inlineformset_factory
from .models import *
from django.utils import timezone
import re

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name',   'category', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter product description', 'rows': 3}),
        }
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not re.search(r'\w', name):
            raise ValidationError("Name cannot be empty, symbols only, or spaces only.")
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or not re.search(r'\w', description):
            raise ValidationError("Description cannot be empty, symbols only, or spaces only.")
        return description  

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['price', 'quantity', 'color']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price','required':'True','min':0}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity','required':'True','min':0}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter color'}),
        }


    def clean_price(self):
        price = self.cleaned_data.get('price')
        print("Price in clean_price:", price) 
        if price is None:
            raise forms.ValidationError("Price cannot be empty")
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        print("Quantity in clean_quantity:", quantity)
        if quantity is None:
            raise ValidationError("Quantity cannot be empty")
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        return quantity
    
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image', 'alt_text']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter alt text'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
        self.fields['image'].required = False
        self.fields['alt_text'].required = False

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file extension
            ext = os.path.splitext(image.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png']
            
            if ext not in allowed_extensions:
                raise forms.ValidationError("Only JPG and PNG files are allowed.")
            
        
        return image 

ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True
)

ProductImageFormSet = inlineformset_factory(
    ProductVariant,
    Image,
    form=ProductImageForm,
    extra=4,  # Allow up to 4 images
    max_num=4,
    can_delete=True
)

class CouponForm(forms.ModelForm):
    
    class Meta:
        model = Coupon
        fields = ["code","discount_type","discount_value","max_total_use","max_use_per_user","expiry_date","min_order_amount"]
        widgets = {
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code or not re.search(r'\w', code):
            raise ValidationError("COde name cannot be empty, symbols only, or spaces only.")
        if len(code)<6:
            raise ValidationError("Code must be atleast 6 characters long")
        return code
    
    def clean_discount_value(self):
        discount_value = self.cleaned_data.get('discount_value')
        if discount_value<0:
            raise ValidationError("Negative values not allowed")
        return discount_value
    
    def clean_max_total_use(self):
        max_total_use = self.cleaned_data.get('max_total_use')
        if max_total_use is not None and max_total_use<=0:
            raise ValidationError("Value must be greater than 0")
        return max_total_use
    
    def clean_max_use_per_user(self):
        max_use_per_user = self.cleaned_data.get('max_use_per_user')
        if max_use_per_user is not None and max_use_per_user<=0:
            raise ValidationError("Value must be greater than 0")
        return max_use_per_user
    
    def clean_min_order_amount(self):
        min_order_amount = self.cleaned_data.get('min_order_amount')
        if min_order_amount and min_order_amount<=0:
            raise ValidationError("Value must be greater than 0")
        return min_order_amount
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date <= timezone.now():
            raise ValidationError("Expiry date must be in the future.")
        return expiry_date
    
class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['name', 'description', 'product', 'discount_percentage', 'discount_amount', 'start_date', 'end_date', 'is_active']

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():  
            raise forms.ValidationError("Name cannot be empty or whitespace.")
        if name.isdigit(): 
            raise forms.ValidationError("Name cannot contain only numbers.")
        if not re.search(r'[a-zA-Z0-9]', name): 
            raise forms.ValidationError("Name must contain at least one alphanumeric character.")
        if len(name) < 4:  
            raise forms.ValidationError("Description must be at least 4 characters long.")
        return name
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description: 
            return description
        if len(description) < 6:  
            raise forms.ValidationError("Description must be at least 6 characters long.")
        if not re.search(r'[a-zA-Z0-9]', description):  
            raise forms.ValidationError("Description cannot consist solely of symbols.")
        return description
    
    def clean_product(self):
        product = self.cleaned_data.get('product')
        if not product:
            raise forms.ValidationError("Product is required.")
        if not Product.objects.filter(id=product.id).exists():
            raise forms.ValidationError("The selected product does not exist.")
        return product
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("Start date must be before end date.")
        return cleaned_data
    
    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage is not None and discount_percentage < 0:
            raise forms.ValidationError("Discount percentage cannot be negative.")
        return discount_percentage

    def clean_discount_amount(self):
        discount_amount = self.cleaned_data.get('discount_amount')
        if discount_amount is not None and discount_amount < 0:
            raise forms.ValidationError("Discount amount cannot be negative.")
        return discount_amount


class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['name', 'description', 'category', 'discount_percentage', 'discount_amount', 'start_date', 'end_date', 'is_active']

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():  
            raise forms.ValidationError("Name cannot be empty or whitespace.")
        if name.isdigit(): 
            raise forms.ValidationError("Name cannot contain only numbers.")
        if not re.search(r'[a-zA-Z0-9]', name): 
            raise forms.ValidationError("Name must contain at least one alphanumeric character.")
        if len(name) < 4:  
            raise forms.ValidationError("Description must be at least 4 characters long.")
        return name
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description: 
            return description
        if len(description) < 6:  
            raise forms.ValidationError("Description must be at least 6 characters long.")
        if not re.search(r'[a-zA-Z0-9]', description):  
            raise forms.ValidationError("Description cannot consist solely of symbols.")
        return description
    
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Product is required.")
        if not Category.objects.filter(id=category.id).exists():
            raise forms.ValidationError("The selected category does not exist.")
        return category
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("Start date must be before end date.")
        return cleaned_data
    
    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage is not None and discount_percentage < 0:
            raise forms.ValidationError("Discount percentage cannot be negative.")
        return discount_percentage

    def clean_discount_amount(self):
        discount_amount = self.cleaned_data.get('discount_amount')
        if discount_amount is not None and discount_amount < 0:
            raise forms.ValidationError("Discount amount cannot be negative.")
        return discount_amount
