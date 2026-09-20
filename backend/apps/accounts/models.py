from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for auth."""
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """Custom User model for SoundSphere supporting email auth."""
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone Number'))
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"


class UserProfile(models.Model):
    """Extended user profile with avatar and extra details."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"Profile of {self.user.email}"


class Address(models.Model):
    """User delivery addresses with unique default address support."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=150, verbose_name=_('Recipient Name'))
    phone = models.CharField(max_length=20, verbose_name=_('Contact Phone'))
    address_line = models.CharField(max_length=255, verbose_name=_('Street Address'))
    city = models.CharField(max_length=100, verbose_name=_('City'))
    district = models.CharField(max_length=100, blank=True, verbose_name=_('State / District / Province'))
    postal_code = models.CharField(max_length=20, verbose_name=_('Postal / ZIP Code'))
    country = models.CharField(max_length=100, default='United States', verbose_name=_('Country'))
    is_default = models.BooleanField(default=False, verbose_name=_('Default Address'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            # Unset default on other addresses of the user
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        elif not Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).exists():
            # If no other default exists, make this one default
            self.is_default = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name}, {self.address_line}, {self.city}"
