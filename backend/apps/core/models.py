from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """Customer support and inquiry messages."""
    name = models.CharField(max_length=150, verbose_name=_('Sender Name'))
    email = models.EmailField(verbose_name=_('Sender Email'))
    phone = models.CharField(max_length=30, blank=True, verbose_name=_('Phone (optional)'))
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message Body'))
    is_read = models.BooleanField(default=False, verbose_name=_('Marked as Read'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at:%b %d, %Y})"


class NewsletterSubscriber(models.Model):
    """Newsletter email subscribers."""
    email = models.EmailField(unique=True, verbose_name=_('Subscriber Email'))
    is_active = models.BooleanField(default=True, verbose_name=_('Subscribed Status'))
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Newsletter Subscriber')
        verbose_name_plural = _('Newsletter Subscribers')
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class Notification(models.Model):
    """User in-app notifications (e.g. order updates, promos)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.email}"
