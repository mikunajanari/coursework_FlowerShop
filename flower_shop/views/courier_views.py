from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json
from django.shortcuts import render

@csrf_exempt
def get_orders(request):
    today_orders = []
    in_progress = []

    with connection.cursor() as cursor:
        # Отримуємо всі доступні замовлення з представлення
        cursor.execute("SELECT order_id, customer_name, phone_number, delivery_address FROM Orders_For_Delivery;")
        rows = cursor.fetchall()
        for row in rows:
            today_orders.append({
                "id": row[0],
                "name": row[1].strip("()").replace(",", " "),
                "phone": row[2],
                "address": row[3]
            })

        # Додатково: замовлення кур’єра, які вже в роботі
        courier_email = request.GET.get("courierEmail")  # формат: example@domain.com
        if courier_email:
            login = courier_email.replace('@', '_')
            cursor.execute("""
                SELECT o.o_kod, c.cust_name, c.phone_number, c.address
                FROM Orders o
                JOIN Customers c ON o.customer = c.kod
                JOIN Couriers cr ON o.courier_id = cr.kod
                WHERE o.order_status = 'в дорозі'
                  AND REPLACE(cr.email, '@', '_') = %s
                  AND o.delivery_date = CURRENT_DATE;
            """, [login])
            for row in cursor.fetchall():
                in_progress.append({
                    "id": row[0],
                    "name": row[1].strip("()").replace(",", " "),
                    "phone": row[2],
                    "address": row[3]
                })

    return JsonResponse({"today": today_orders, "inProgress": in_progress})

@csrf_exempt
def accept_order(request, order_id):
    try:
        # Викликаємо збережену функцію, яка:
        # 1. Знаходить кур’єра за SESSION_USER (тобто логіном)
        # 2. Призначає його
        with connection.cursor() as cursor:
            cursor.execute("SELECT assign_courier_to_order(%s);", [order_id])
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@csrf_exempt
def complete_order(request, order_id):
    try:
        # Кур'єр змінює лише статус — БД через тригер сама перевірить право
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE Orders
                SET order_status = 'доставлено'
                WHERE o_kod = %s;
            """, [order_id])
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)