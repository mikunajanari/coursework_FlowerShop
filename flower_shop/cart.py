# cart.py — логіка кошика через сесію
from decimal import Decimal
import decimal
from django.conf import settings
from flower_shop.models import Product
from django.db import connection

CART_SESSION_ID = 'cart'

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.kod)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()


    def save(self):
        for item in self.cart.values():
            if isinstance(item['price'], decimal.Decimal):
                item['price'] = float(item['price'])
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.kod)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(kod__in=product_ids)
        cart = self.cart.copy()
        # Створюємо проміжний словник для відповідності id -> product
        products_map = {str(product.kod): product for product in products}
        for product_id, item in cart.items():
            item = item.copy()
            product = products_map[product_id]
            item['product'] = product
            
            # Додаємо правильну доступну кількість
            with connection.cursor() as cursor:
                cursor.execute("SELECT available_amount FROM Available_Products_For_Guests WHERE product_id = %s", [product.kod])
                row = cursor.fetchone()
                if row:
                    product.flower_available = row[0]  # Це буде використано в шаблоні
            
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[CART_SESSION_ID]
        self.session.modified = True
    
    def get_quantity(self, product):
        for item in self:
            if item['product'].kod == product.kod:
                return item['quantity']
        return 0
    
    def get_quantity_by_id(self, product_id):
        for item in self:
            # Порівнюємо і за id, і за kod для універсальності
            if (hasattr(item['product'], 'id') and str(item['product'].id) == str(product_id)) or \
               (hasattr(item['product'], 'kod') and str(item['product'].kod) == str(product_id)):
                return item['quantity']
        return 0