from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating_stars', 'title', 'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    list_editable = ('is_approved',)
    actions = ['approve_reviews', 'reject_reviews']

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color:#ffb300; font-size:14px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'

    @admin.action(description=_('Approve selected reviews'))
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        # Update ratings for affected products
        for review in queryset:
            review.product.update_rating()

    @admin.action(description=_('Reject selected reviews'))
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        for review in queryset:
            review.product.update_rating()
