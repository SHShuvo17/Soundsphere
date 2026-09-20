from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User
from apps.accounts.models import Address
from apps.catalog.models import Brand, Category, Product, ProductType
from apps.orders.models import Order, OrderItem, Payment
from apps.reviews.models import Review


class PanelAccessTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user('customer@example.com', 'customer', 'password123')
        self.other_customer = User.objects.create_user('other@example.com', 'other', 'password123')
        self.staff = User.objects.create_user('staff@example.com', 'staff', 'password123', is_staff=True)
        self.brand = Brand.objects.create(name='Test Audio', slug='test-audio')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product_type = ProductType.objects.create(category=self.category, name='Test Type', slug='test-type')
        self.product = Product.objects.create(
            name='Test Speaker', slug='test-speaker', sku='TEST-001', brand=self.brand,
            category=self.category, product_type=self.product_type, short_description='Short',
            description='Description', price=Decimal('100.00'), stock_quantity=5,
        )
        self.order = Order.objects.create(
            user=self.customer, shipping_address_snapshot={'full_name': 'Customer'},
            subtotal=Decimal('100.00'), total_amount=Decimal('100.00'),
        )
        OrderItem.objects.create(order=self.order, product=self.product, product_name_snapshot=self.product.name,
                                 sku_snapshot=self.product.sku, price_snapshot=self.product.price,
                                 quantity=1, subtotal=self.product.price)
        Payment.objects.create(order=self.order, payment_method='COD', amount=self.order.total_amount)

    def test_staff_dashboard_is_staff_only(self):
        self.client.login(username='customer@example.com', password='password123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='staff@example.com', password='password123')
        self.assertEqual(self.client.get(reverse('dashboard:index')).status_code, 200)

    def test_customer_cannot_view_another_customers_order(self):
        self.client.login(username='other@example.com', password='password123')
        response = self.client.get(reverse('orders:detail', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 404)

    def test_staff_can_update_order_and_payment_status(self):
        self.client.login(username='staff@example.com', password='password123')
        response = self.client.post(reverse('dashboard:order_status', args=[self.order.order_number]), {
            'order_status': Order.OrderStatus.SHIPPED,
            'payment_status': Order.PaymentStatus.PAID,
        })
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, Order.OrderStatus.SHIPPED)
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)
        self.assertEqual(self.order.payment.status, Order.PaymentStatus.PAID)

    def test_staff_can_set_delivered_without_overwriting_selected_payment_status(self):
        self.client.login(username='staff@example.com', password='password123')
        self.client.post(reverse('dashboard:order_status', args=[self.order.order_number]), {
            'order_status': Order.OrderStatus.DELIVERED,
            'payment_status': Order.PaymentStatus.PENDING,
        })
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, Order.OrderStatus.DELIVERED)
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PENDING)
        self.assertEqual(self.order.payment.status, Order.PaymentStatus.PENDING)

    def test_customer_can_edit_and_delete_only_owned_address(self):
        address = Address.objects.create(user=self.customer, full_name='Customer', phone='123', address_line='Old Street', city='Austin', postal_code='78701')
        other_address = Address.objects.create(user=self.other_customer, full_name='Other', phone='456', address_line='Other Street', city='Dallas', postal_code='75001')
        self.client.login(username='customer@example.com', password='password123')
        response = self.client.post(reverse('accounts:address_edit', args=[address.pk]), {
            'full_name': 'Updated Customer', 'phone': '123', 'address_line': 'New Street',
            'city': 'Austin', 'district': '', 'postal_code': '78701', 'country': 'United States', 'is_default': 'on',
        })
        self.assertRedirects(response, reverse('accounts:addresses'))
        address.refresh_from_db()
        self.assertEqual(address.address_line, 'New Street')
        self.assertEqual(self.client.post(reverse('accounts:address_delete', args=[other_address.pk])).status_code, 404)
        self.assertTrue(Address.objects.filter(pk=other_address.pk).exists())

    def test_staff_can_create_category_but_customer_cannot(self):
        data = {'name': 'New Category', 'slug': 'new-category', 'is_active': 'on'}
        self.client.login(username='customer@example.com', password='password123')
        self.assertEqual(self.client.post(reverse('dashboard:resource_create', args=['categories']), data).status_code, 302)
        self.client.login(username='staff@example.com', password='password123')
        response = self.client.post(reverse('dashboard:resource_create', args=['categories']), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(slug='new-category').exists())

    def test_review_requires_delivered_purchase(self):
        self.client.login(username='customer@example.com', password='password123')
        response = self.client.post(reverse('reviews:submit', args=[self.product.pk]), {
            'rating': 5, 'title': 'Great', 'comment': 'Sounds good',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(user=self.customer, product=self.product).exists())

    def test_customer_can_review_a_delivered_purchase(self):
        self.order.order_status = Order.OrderStatus.DELIVERED
        self.order.save(update_fields=['order_status', 'updated_at'])
        self.client.login(username='customer@example.com', password='password123')
        response = self.client.post(reverse('reviews:submit', args=[self.product.pk]), {
            'rating': 5, 'title': 'Great', 'comment': 'Sounds good',
        })
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get(user=self.customer, product=self.product)
        self.assertTrue(review.is_verified_purchase)
        self.assertFalse(review.is_approved)