from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from flower_shop.models import Product  # Замініть на вашу модель товару
from flower_shop.cart import Cart
from django.db import connection
import json

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, kod=product_id)
    
    # Отримуємо правильну доступну кількість через SQL-запит
    with connection.cursor() as cursor:
        cursor.execute("SELECT available_amount FROM Available_Products_For_Guests WHERE product_id = %s", [product_id])
        row = cursor.fetchone()
        available_amount = row[0] if row else 0
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Обчислюємо скільки ми можемо додати (враховуючи кошик)
        in_cart_quantity = cart.get_quantity_by_id(product_id)
        can_add = available_amount - in_cart_quantity
        
        # Обмежуємо нову кількість
        if quantity > can_add:
            quantity = can_add if can_add > 0 else 0
            
        if quantity > 0:
            cart.add(product=product, quantity=quantity, update_quantity=False)
            
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, kod=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    # Для діагностики виведіть структуру першого елемента кошика
    debug_info = {}
    if len(cart) > 0:
        for item in cart:
            debug_info = {
                'product_id': item['product'].kod,
                'quantity': item['quantity'],
                'flower_amount': item['product'].flower.amount if hasattr(item['product'], 'flower') else 'N/A',
                'available_amount': item['product'].available_amount if hasattr(item['product'], 'available_amount') else 'N/A'
            }
            break
    
    return render(request, 'flower_shop/cart.html', {'cart': cart, 'debug_info': debug_info})

def cart_update_quantity(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, kod=product_id)
    
    # Отримуємо правильне значення доступної кількості
    with connection.cursor() as cursor:
        cursor.execute("SELECT available_amount FROM Available_Products_For_Guests WHERE product_id = %s", [product_id])
        row = cursor.fetchone()
        available_amount = row[0] if row else 0
    
    if request.method == 'POST':
        try:
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity < 1:
                new_quantity = 1
                
            # Суворе обмеження максимальною кількістю
            if new_quantity > available_amount:
                new_quantity = available_amount
                
        except (ValueError, TypeError):
            new_quantity = 1
            
        cart.add(product=product, quantity=new_quantity, update_quantity=True)
    return redirect('cart_detail')

@require_POST
def sync_cart(request):
    """Синхронізує кошик з клієнта з серверним кошиком"""
    try:
        data = json.loads(request.body)
        if not isinstance(data, list):
            return JsonResponse({'error': 'Невалідний формат даних'}, status=400)
        
        # Отримуємо серверний кошик
        cart = Cart(request)
        
        # Очищаємо серверний кошик перед синхронізацією
        cart.clear()
        
        # Додаємо товари з клієнтського кошика у серверний
        for item in data:
            product_id = item.get('id')
            quantity = item.get('quantity', 1)
            
            if not product_id or quantity <= 0:
                continue
                
            product = Product.objects.filter(kod=product_id).first()
            if not product:
                continue
                
            # Додаємо товар у кошик
            cart.add(product=product, quantity=quantity, update_quantity=True)
        
        return JsonResponse({
            'success': True,
            'cart_size': len(cart),
            'total_price': str(cart.get_total_price())
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Невалідний JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
