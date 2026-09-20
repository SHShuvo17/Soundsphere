from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Main audio category (e.g. Bluetooth Speakers, Soundbars, Home Theater)."""
    name = models.CharField(max_length=150, unique=True, verbose_name=_('Category Name'))
    slug = models.SlugField(max_length=170, unique=True, db_index=True)
    description = models.TextField(blank=True, verbose_name=_('Description'))
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon_svg = models.TextField(blank=True, help_text=_('SVG icon code for header/cards'))
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    """Sub-type under a Category (e.g. Portable Bluetooth Speaker, Dolby Atmos Soundbar)."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_types')
    name = models.CharField(max_length=150, verbose_name=_('Product Type Name'))
    slug = models.SlugField(max_length=170, unique=True, db_index=True)
    description = models.TextField(blank=True, verbose_name=_('Description'))
    image = models.ImageField(upload_to='product_types/', blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product Type')
        verbose_name_plural = _('Product Types')
        ordering = ['category', 'name']
        constraints = [
            models.UniqueConstraint(fields=['category', 'name'], name='unique_category_product_type')
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.slug}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Brand(models.Model):
    """Audio manufacturer brand (e.g. JBL, Sony, Bose, Marshall)."""
    name = models.CharField(max_length=150, unique=True, verbose_name=_('Brand Name'))
    slug = models.SlugField(max_length=170, unique=True, db_index=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True, verbose_name=_('Description'))
    website = models.URLField(blank=True, verbose_name=_('Official Website'))
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product entity for SoundSphere audio equipment."""
    name = models.CharField(max_length=255, verbose_name=_('Product Name'), db_index=True)
    slug = models.SlugField(max_length=280, unique=True, db_index=True)
    sku = models.CharField(max_length=60, unique=True, db_index=True, verbose_name=_('SKU Code'))
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name='products')
    
    short_description = models.TextField(max_length=500, verbose_name=_('Short Summary'))
    description = models.TextField(verbose_name=_('Full Product Description'))
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))], 
        verbose_name=_('Regular Price ($)')
    )
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(Decimal('0.00'))], 
        verbose_name=_('Discount Price ($)')
    )
    
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Available Stock Quantity'))
    low_stock_threshold = models.PositiveIntegerField(default=5, verbose_name=_('Low Stock Alert Threshold'))
    warranty = models.CharField(max_length=150, default='1 Year Official Warranty', verbose_name=_('Warranty'))
    
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Average Rating'))
    review_count = models.PositiveIntegerField(default=0, verbose_name=_('Review Count'))
    sold_count = models.PositiveIntegerField(default=0, verbose_name=_('Units Sold'))
    
    # Badges & Flags
    is_featured = models.BooleanField(default=False, db_index=True, verbose_name=_('Featured on Homepage'))
    is_best_seller = models.BooleanField(default=False, db_index=True, verbose_name=_('Best Seller'))
    is_new_arrival = models.BooleanField(default=True, db_index=True, verbose_name=_('New Arrival'))
    is_on_sale = models.BooleanField(default=False, db_index=True, verbose_name=_('On Sale Flag'))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_('Active Status'))
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'product_type', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['price', 'rating']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")
        
        # Auto sync on_sale flag
        if self.discount_price and self.discount_price > 0 and self.discount_price < self.price:
            self.is_on_sale = True
        else:
            self.is_on_sale = False
            
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        """Returns the active checkout price (discounted or regular)."""
        if self.discount_price and self.discount_price > 0 and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def discount_percentage(self):
        """Calculates discount percentage for badge display."""
        if self.discount_price and self.discount_price > 0 and self.discount_price < self.price:
            diff = self.price - self.discount_price
            return int(round((diff / self.price) * 100))
        return 0

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def stock_status(self):
        if self.stock_quantity <= 0:
            return 'out_of_stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            return 'low_stock'
        return 'in_stock'

    @property
    def stock_status_display(self):
        if self.stock_quantity <= 0:
            return 'Out of Stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            return f'Low Stock ({self.stock_quantity} left)'
        return f'In Stock ({self.stock_quantity} available)'

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if not primary:
            primary = self.images.first()
        return primary

    def update_rating(self):
        """Recalculates rating and review_count from approved reviews."""
        from apps.reviews.models import Review
        reviews = Review.objects.filter(product=self, is_approved=True)
        self.review_count = reviews.count()
        if self.review_count > 0:
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0
            self.rating = round(Decimal(str(avg)), 2)
        else:
            self.rating = Decimal('0.00')
        self.save(update_fields=['rating', 'review_count'])

    def __str__(self):
        return f"{self.brand.name} {self.name} (${self.effective_price})"


class ProductImage(models.Model):
    """Multiple images per audio product with primary selector."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, help_text=_('Fallback or external image URL'))
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['-is_primary', 'display_order', 'id']

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    @property
    def url(self):
        if self.image and bool(self.image.name):
            try:
                return self.image.url
            except ValueError:
                pass
        return self.image_url or '/static/images/placeholder-speaker.svg'

    def __str__(self):
        return f"Image for {self.product.name} (order: {self.display_order})"


class ProductSpecification(models.Model):
    """Dynamic key-value specifications for audio gear (e.g. Power Output, Battery, IPX)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    specification_name = models.CharField(max_length=120, verbose_name=_('Specification Name'))
    specification_value = models.CharField(max_length=255, verbose_name=_('Specification Value'))
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Product Specification')
        verbose_name_plural = _('Product Specifications')
        ordering = ['display_order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['product', 'specification_name'], name='unique_product_specification_name')
        ]

    def __str__(self):
        return f"{self.specification_name}: {self.specification_value}"
