from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, Address


class UserRegistrationForm(forms.ModelForm):
    """User registration form with email, username, names, phone, and password confirmation."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create strong password (min 8 chars)',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }),
        label=_('Password'),
        help_text=_('Must be at least 8 characters long.')
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }),
        label=_('Confirm Password')
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com', 'class': 'form-control'}),
            'username': forms.TextInput(attrs={'placeholder': 'e.g. audiophile99', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': '+1 (555) 000-0000', 'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('An account with this email address already exists.'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_('This username is already taken. Please choose another.'))
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', _('Passwords do not match.'))
            else:
                # Run Django password validators
                password_validation.validate_password(password, self.instance)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user


class UserLoginForm(forms.Form):
    """User login supporting either email or username."""
    identifier = forms.CharField(
        label=_('Email or Username'),
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your email or username',
            'class': 'form-control',
            'autocomplete': 'username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Remember me for 30 days')
    )

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('identifier')
        password = cleaned_data.get('password')

        if identifier and password:
            self.user = authenticate(username=identifier, password=password)
            if self.user is None:
                raise forms.ValidationError(_('Invalid credentials. Please verify your email/username and password.'))
            if not self.user.is_active:
                raise forms.ValidationError(_('This account is currently disabled. Please contact support.'))
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)


class UserProfileForm(forms.ModelForm):
    """Update profile and contact information."""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AddressForm(forms.ModelForm):
    """Delivery address creation and editing."""
    class Meta:
        model = Address
        fields = ('full_name', 'phone', 'address_line', 'city', 'district', 'postal_code', 'country', 'is_default')
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-control'}),
            'address_line': forms.TextInput(attrs={'placeholder': 'Street Address & Apt / Suite', 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'City', 'class': 'form-control'}),
            'district': forms.TextInput(attrs={'placeholder': 'State / Province', 'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'ZIP / Postal Code', 'class': 'form-control'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country', 'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
