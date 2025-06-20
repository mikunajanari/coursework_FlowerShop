from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import connection
import datetime

def checkout(request):
    from flower_shop.cart import Cart
    cart = Cart(request)
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
    return render(request, 'flower_shop/checkout.html', {'cart': cart, 'user_data': user_data})

@require_POST
def place_order(request):
    from flower_shop.cart import Cart
    cart = Cart(request)
    
    print("Запит на створення замовлення отримано")
    
    if len(cart) == 0:
        print("Помилка: кошик порожній")
        return JsonResponse({'error': 'Кошик порожній'}, status=400)
    
    # Отримуємо користувача
    user_login = request.user.username if request.user.is_authenticated else request.session.get('pg_user')
    print(f"Користувач: {user_login}")
    
    if not user_login:
        print("Помилка: користувач не авторизований")
        return JsonResponse({'error': 'Увійдіть у систему'}, status=401)
    
    # Встановлюємо дату доставки на 3 дні вперед
    delivery_date = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
    delivery_method = 'courier'
    
    # Підготовка елементів замовлення
    order_items = []
    for item in cart:
        order_items.append({
            'flower_id': item['product'].kod,
            'amount': item['quantity']
        })
    
    try:
        with connection.cursor() as cursor:
            # Все ще встановлюємо ROLE для правильних дозволів
            cursor.execute(f"SET ROLE {user_login}")
            
            # Підготовка SQL-виклику з параметрами, передаємо user_login як перший параметр
            sql = "SELECT create_order_for_current_user(%s, %s, %s"
            params = [user_login, delivery_date, delivery_method]
            
            # Додаємо кожен елемент як параметр
            for item in order_items:
                sql += ", ROW(%s, %s)::flower_order"
                params.extend([item['flower_id'], item['amount']])
            
            sql += ")"
            
            print(f"SQL: {sql}")
            print(f"Параметри: {params}")
            
            # Виконання функції
            cursor.execute(sql, params)
            result = cursor.fetchone()
            
            if result is None:
                print("Помилка: функція не повернула ID замовлення")
                return JsonResponse({'error': 'Помилка створення замовлення'}, status=500)
                
            order_id = result[0]
            print(f"Створено замовлення з ID: {order_id}")
            
            # Очищаємо кошик після успішного замовлення
            cart.clear()
            
            # Зберігаємо ID замовлення в сесії для сторінки підтвердження
            request.session['last_order_id'] = order_id
            
            return JsonResponse({'success': True, 'order_id': order_id})
            
    except Exception as e:
        import traceback
        print("Помилка при створенні замовлення:")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


def order_confirmation(request):
    order_id = request.session.get('last_order_id')
    if not order_id:
        print("Помилка: немає ID замовлення в сесії")
        return redirect('shop')
    
    print(f"Відображення підтвердження для замовлення: {order_id}")
    return render(request, 'flower_shop/confirmation.html', {
        'order_id': order_id
    })