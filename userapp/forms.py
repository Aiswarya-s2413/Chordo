from django import forms
from adminapp.models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
import re

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'name', 'gender', 'email', 'phone_number'] 

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control custom-input', 
                'placeholder': 'Enter your name', 
                'style': 'height:50px;'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'readonly': 'readonly',
                'style': 'height:50px;'  
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control custom-input', 
                'placeholder': 'Enter phone number', 
                'style': 'height:50px;'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'style': 'height:50px;' 
            }),
        }
    
            
    def clean_name(self):
            name = self.cleaned_data.get('name')

            if not name:
                raise ValidationError("Name is required.")

            if len(name) < 4:
                raise ValidationError("Name is too short. It must have at least 4 characters.")

            if not re.match(r'^[A-Za-z\s]+$', name):
                raise ValidationError("Name can only contain letters and spaces.")

            return name        
         

    def clean_phone_number(self):
            phone_number = self.cleaned_data.get('phone_number')
            user_id = self.instance.user.id  #user ID of the current profile being edited

            if Profile.objects.filter(phone_number=phone_number).exclude(user__id=user_id).exists():
                raise ValidationError('This phone number already exists.')
            
            if not phone_number:
                 raise ValidationError('Phone number is required')

            if not phone_number.isdigit():
                 raise ValidationError('Enter a valid phone number')

            if len(phone_number)!=10:
                 raise ValidationError('Phone number should contain 10 digits')

            if phone_number == '0000000000':
                 raise ValidationError("Phone number should not contain only zeroes") 

            return phone_number
    
    
    def clean(self):
            cleaned_data = super().clean()
            return cleaned_data
            

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'city', 'state', 'country', 'pincode', 'is_primary']
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    
    def clean_address_line1(self):
        address_line1 = self.cleaned_data.get('address_line1')
        if len(address_line1) < 5:
            raise ValidationError('Address Line 1 should be at least 5 characters long.')
        if not address_line1.isalnum() and not re.match(r'^[a-zA-Z0-9\s]+$', address_line1):
            raise ValidationError('Address Line 1 can only contain letters and spaces.')
        return address_line1
    
    def clean_address_line2(self):
        address_line2 = self.cleaned_data.get('address_line2')
        if address_line2 and not address_line2.isalnum() and not re.match(r'^[a-zA-Z0-9\s]+$', address_line2):
            raise ValidationError('Address Line 2 can only contain letters and spaces.')
        return address_line2

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city.isalpha():
            raise ValidationError('City should contain only alphabets.')
        return city
    
    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state.isalpha():
            raise ValidationError('State should contain only alphabets.')
        return state

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country.isalpha():
            raise ValidationError('Country should contain only alphabets.')
        return country

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode.isdigit():
            raise ValidationError('Pincode should contain only digits.')
        if len(pincode) != 6:
            raise ValidationError('Pincode must be 6 digits long.')
        if pincode == '000000':
            raise ValidationError('Pincode cannot be entirely 0.')
        return pincode

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )

    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']


class ReviewForm(forms.ModelForm):
    class Meta:
          model = Review
          fields = ['comment','rating']
          widgets = {
               'comment' : forms.Textarea(attrs={'class': 'form-control','rows':3, 'placeholder': 'Write your review here...'}),
               'rating' : forms.NumberInput(attrs={'class': 'form-control','min': 1,'max': 5, 'placeholder':'Rate from 1 to 5'})
          }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        
        if not comment:
            raise ValidationError('Comment cannot be empty.')
        
        if len(comment) < 6:
            raise ValidationError('Comment must be at least 6 characters long.')
        
        if not re.search(r'[A-Za-z0-9]', comment):
            raise ValidationError('Comment must contain at least one letter or number, not just symbols.')
        
        return comment

    