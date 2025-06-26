from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import connection
import datetime
import json
import logging

logger = logging.getLogger(__name__)

def checkout(request):
    if not request.session.get('pg_user'):
        return redirect('login')
    
    from flower_shop.cart import Cart
    
    cart = Cart(request)
    cart_json = '{}'
    
    try:
        if hasattr(cart, 'cart') and cart.cart:
            cart_json = json.dumps(cart.cart)
    except Exception as e:
        logger.error(f"Помилка при серіалізації кошика: {str(e)}")
    
    user_data = {}
    user_login = request.user.username if request.user.is_authenticated else request.session.get('pg_user')
    if user_login:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_profile_by_login(%s)", [user_login])
            row = cursor.fetchone()
            if row:
                user_data = {
                    'first_name': row[0],
                    'surname': row[1],
                    'middle_name': row[2],
                    'phone': row[3],
                    'email': row[4],
                    'photo_link': row[5],
                    'city': row[6],
                    'street': row[7],
                    'house': row[8],
                    'flat': row[9],
                }
    return render(request, 'flower_shop/checkout.html', {
        'cart': cart, 
        'cart_json': cart_json,
        'user_data': user_data
    })

@require_POST
def place_order(request):
    from flower_shop.cart import Cart
    
    cart = Cart(request)
    
    if len(cart) == 0 or not getattr(cart, 'cart', None):
        logger.warning("Спроба оформити замовлення з порожнім кошиком")
        return JsonResponse({'error': 'Кошик порожній або не містить жодного товару'}, status=400)
    
    user_login = request.user.username if request.user.is_authenticated else request.session.get('pg_user')
    
    if not user_login:
        logger.warning("Спроба оформити замовлення без авторизації")
        return JsonResponse({'error': 'Увійдіть у систему'}, status=401)
    
    delivery_date = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
    delivery_method = request.GET.get('deliveryMethod', 'самовивіз')
    
    order_items = []
    for item in cart:
        flower_id = item['product'].kod
        quantity = item['quantity']
        order_items.append({
            'flower_id': flower_id,
            'amount': quantity
        })
    
    try:
        flower_orders = '{' + ','.join([f'"({item["flower_id"]},{item["amount"]})"' for item in order_items]) + '}'
        
        with connection.cursor() as cursor:
            cursor.execute(f'SET ROLE "{user_login}"')
            
            cursor.execute(
                "SELECT create_order_for_current_user(%s::text, %s::date, %s::varchar, VARIADIC %s::flower_order[])",
                [user_login, delivery_date, delivery_method, flower_orders]
            )
            
            result = cursor.fetchone()
            
            if result is None:
                logger.error("Функція БД не повернула ID замовлення")
                return JsonResponse({'error': 'Помилка створення замовлення'}, status=500)
                
            order_id = result[0]
            logger.info(f"Створено замовлення #{order_id} для користувача {user_login}")
            
            # Очищаємо кошик після успішного замовлення
            cart.clear()
            
            # Зберігаємо ID замовлення в сесії для сторінки підтвердження
            request.session['last_order_id'] = order_id
            
            return JsonResponse({'success': True, 'order_id': order_id})
            
    except Exception as e:
        logger.error(f"Помилка при створенні замовлення: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def order_confirmation(request):
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('shop')
    
    return render(request, 'flower_shop/confirmation.html', {
        'order_id': order_id
    })