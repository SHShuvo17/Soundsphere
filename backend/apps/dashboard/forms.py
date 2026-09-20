from django import forms

from apps.catalog.models import Brand, Category, Product, ProductType
from apps.promotions.models import Coupon


class StaffProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('is_on_sale', 'rating', 'review_count', 'sold_count', 'created_at', 'updated_at')


class StaffCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'slug', 'description', 'image', 'icon_svg', 'is_active')


class StaffProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ('category', 'name', 'slug', 'description', 'image', 'is_active')


class StaffBrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ('name', 'slug', 'logo', 'description', 'website', 'is_active')


class StaffCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('code', 'discount_type', 'discount_value', 'min_purchase_amount', 'max_discount_amount',
                  'usage_limit', 'usage_per_user', 'valid_from', 'valid_to', 'is_active')
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }