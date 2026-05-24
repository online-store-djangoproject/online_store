# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
# from cors.models import User
from products.models import Category,Product,Review
from orders.models import Cart, Cartitems,Order, OrderItem



from userprofile.models import Address, DiscountCode

import uuid

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='12345', first_name='Ali', last_name='Rezaei')

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)
        self.assertEqual(str(self.user), f'{self.user.email},{self.user.phone},{self.user.get_full_name()}')

    def test_user_tokens(self):
        tokens = self.user.tokens()
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)


class AddressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test2@example.com', password='12345')
        self.address = Address.objects.create(
            user=self.user,
            city='Tehran',
            state='Tehran',
            full_address='Valiasr St',
            postal_code='1234567890'
        )

    def test_address_str(self):
        self.assertEqual(str(self.address), f"{self.user.email},Tehran, Tehran")


class DiscountCodeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test3@example.com', password='12345')
        self.code = DiscountCode.objects.create(user=self.user, code='OFF15', percentage=15)

    def test_discount_code_str(self):
        self.assertEqual(str(self.code), f"OFF15 - {self.user.email}")

    def test_user_can_get_discount(self):
        can_get = DiscountCode.user_can_get_discount(self.user)
        self.assertFalse(can_get)  # چون همین الان کد گرفته

class CategoryTestCase(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(
            title="Electronics",
            slug="electronics"
        )
        self.assertEqual(category.title, "Electronics")
        self.assertEqual(category.slug, "electronics")
        self.assertIsNotNone(category.category_id)  # اطمینان از اینکه category_id ایجاد شده


from django.utils.text import slugify

class ReviewTestCase(TestCase):

    def setUp(self):
        # ایجاد یک محصول برای تست و تعیین مقدار slug
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description",
            price=100.0,
            slug=slugify("Test Product")  # تعیین مقدار slug
        )

        # ایجاد یک بررسی برای محصول
        self.review = Review.objects.create(
            product=self.product,
            description="This is a great product!",
            name="John Doe"
        )

class ProductTestCase(TestCase):

    def setUp(self):
        self.category = Category.objects.create(title="Electronics", slug="electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description",
            price=100.0,
            category=self.category,
            slug="test-product"
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.category.title, "Electronics")
        self.assertEqual(self.product.price, 100.0)
        self.assertEqual(self.product.slug, "test-product")
        self.assertEqual(self.product.inventory, 5)  # مقدار پیش‌فرض برای موجودی



class CartTestCase(TestCase):

    def setUp(self):
        self.cart = Cart.objects.create()

    def test_cart_creation(self):
        self.assertIsNotNone(self.cart.id)  # بررسی که id ایجاد شده است
        self.assertIsInstance(self.cart.created, type(self.cart.created))  # بررسی نوع تاریخ ایجاد


class OrderTestCase(TestCase):
    def setUp(self):
        # ایجاد یک کاربر برای سفارش با ایمیل (بدون username)
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        # ایجاد یک دسته‌بندی برای محصول
        self.category = Category.objects.create(
            title="Test Category",
            slug="test-category"
        )

        # ایجاد یک محصول برای سفارش
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description",
            price=100.0,
            category=self.category,
            slug="test-product"
        )

        # ایجاد یک سفارش برای کاربر
        self.order = Order.objects.create(owner=self.user)
    def test_order_creation(self):
        # بررسی ایجاد یک سفارش
        self.assertEqual(self.order.owner, self.user)
        self.assertEqual(self.order.pending_status, Order.PAYMENT_STATUS_PENDING)

    def test_order_item_addition(self):
        # ایجاد یک آیتم برای سفارش
        order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2)

        # بررسی اضافه شدن آیتم به سفارش
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)

        # بررسی تعداد آیتم‌ها در سفارش
        self.assertEqual(self.order.items.count(), 1)

    def test_update_total_amount(self):
        # ایجاد آیتم‌هایی برای سفارش
        OrderItem.objects.create(order=self.order, product=self.product, quantity=2)
        OrderItem.objects.create(order=self.order, product=self.product, quantity=3)

        # به‌روزرسانی مبلغ کل سفارش
        self.order.update_total_amount()

        # بررسی مبلغ کل سفارش
        expected_total = (2 * self.product.price) + (3 * self.product.price)
        self.assertEqual(self.order.total_amount, expected_total)

    def test_order_str_method(self):
        # بررسی متد __str__ برای نمایش وضعیت سفارش
        self.order.pending_status = Order.PAYMENT_STATUS_COMPLETE
        self.order.save()
        self.assertEqual(str(self.order), f'{self.order.pending_status}, Order {self.order.id} - Status: Complete')

    def test_order_payment_status_choices(self):
        # بررسی انتخاب‌های وضعیت پرداخت
        self.assertEqual(self.order.PAYMENT_STATUS_PENDING, 'P')
        self.assertEqual(self.order.PAYMENT_STATUS_COMPLETE, 'C')
        self.assertEqual(self.order.PAYMENT_STATUS_FAILED, 'F')

    def test_order_item_str_method(self):
        # بررسی متد __str__ برای نمایش نام محصول در آیتم سفارش
        order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2)
        self.assertEqual(str(order_item), self.product.name)

# class CategoryProductReviewTest(TestCase):
#     def setUp(self):
#         self.category = Category.objects.create(title="Electronics", slug="electronics")
#         self.product = Product.objects.create(name="Phone", price=300.0, category=self.category)
#         self.review = Review.objects.create(product=self.product, name="Reza", description="Great!")
#
#     def test_product_str(self):
#         self.assertEqual(str(self.product), "Phone")
#
#     def test_review_str(self):
#         self.assertEqual(str(self.review), "Great!")
#
#     def test_category_str(self):
#         self.assertEqual(str(self.category), "Electronics")


# class CartTest(TestCase):
#     def setUp(self):
#         self.cart = Cart.objects.create()
#         self.category = Category.objects.create(title="Accessories")
#         self.product = Product.objects.create(name="Charger", price=50, category=self.category)
#         self.item = Cartitems.objects.create(cart=self.cart, product=self.product, quantity=2)
#
#     def test_cartitem_total_price(self):
#         self.assertEqual(self.item.quantity, 2)
#         self.assertEqual(str(self.cart), str(self.cart.id))
#

# class OrderTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(email='order@test.com', password='12345')
#         self.category = Category.objects.create(title="Books")
#         self.product = Product.objects.create(name="Book 1", price=200, category=self.category)
#         self.order = Order.objects.create(owner=self.user)
#         self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=3)
#
#     def test_order_str(self):
#         status_display = self.order.get_pending_status_display()
#         self.assertIn(status_display, str(self.order))
#
#     def test_orderitem_str(self):
#         self.assertEqual(str(self.order_item), "Book 1")
#
#     def test_update_total_amount(self):
#         self.order.update_total_amount()
#         self.assertEqual(self.order.total_amount, 600)
