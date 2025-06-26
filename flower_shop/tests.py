from django.test import TestCase, Client
from django.db import connection
from flower_shop.models import Product, Planted, Species, Genera, Customers

class CartGuestTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.genera, _ = Genera.objects.get_or_create(genus_name="Тестовий рід")
        self.species, _ = Species.objects.get_or_create(
            species_name="Тестовий вид",
            genus=self.genera,
            instruction="Тестова інструкція",
            storage_period=10,
            photo_link="http://example.com/photo.jpg"
        )
        self.planted = Planted.objects.create(
            flower=self.species,
            amount=10
        )
        self.product = Product.objects.create(
            flower=self.planted,
            price=100
        )

    def test_guest_can_add_product_to_cart(self):
        response = self.client.post(f'/cart/add/{self.product.kod}/', {'quantity': 2}, follow=True)
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        cart = session.get('cart')
        self.assertIsNotNone(cart)
        self.assertIn(str(self.product.kod), cart)
        self.assertEqual(cart[str(self.product.kod)]['quantity'], 2)

    def test_cannot_add_more_than_available(self):
        response = self.client.post(f'/cart/add/{self.product.kod}/', {'quantity': 15}, follow=True)
        session = self.client.session
        cart = session.get('cart')
        self.assertLessEqual(cart[str(self.product.kod)]['quantity'], self.planted.amount)


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_creates_new_user(self):
        signup_data = {
            "first_name": "Тест",
            "surname": "Користувач",
            "middle_name": "Тестович",
            "phone": "+380 (67) 000 0000",
            "email": "testuser@example.com",
            "city": "Київ",
            "street": "Тестова",
            "house": 1,
            "flat": 2,
            "password": "testpassword123",
            "password2": "testpassword123",
        }
        response = self.client.post('/signup/', signup_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Customers.objects.filter(email="testuser@example.com").exists())
        username = signup_data["email"].replace("@", "_")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [username])
            self.assertTrue(cursor.fetchone(), msg="PostgreSQL role for user was not created")