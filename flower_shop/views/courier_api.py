from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import connection
import json

@require_GET
def orders_for_delivery(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT order_id, (customer_name).surname, (customer_name).firstname, (customer_name).middlename,
                   phone_number, (delivery_address).city, (delivery_address).street, (delivery_address).house, (delivery_address).flat
            FROM Orders_For_Delivery
        """)
        rows = cursor.fetchall()
        print("rows:", rows)
    data = [
        {
            'order_id': row[0],
            'surname': row[1],
            'firstname': row[2],
            'middlename': row[3],
            'phone': row[4],
            'city': row[5],
            'street': row[6],
            'house': row[7],
            'flat': row[8]
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def assign_courier(request):
    try:
        data = json.loads(request.body)
        order_id = data.get("order_id")
        if not order_id:
            return HttpResponseBadRequest("Не вказано замовлення")
        with connection.cursor() as cursor:
            cursor.execute("SELECT assign_courier_to_order(%s)", [order_id])
        return JsonResponse({"success": True})
    except Exception as e:
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type="application/json")
    
@require_GET
def orders_taken_by_courier(request):
    login = request.session.get('pg_user')
    if not login:
        return JsonResponse({'error': 'Неавторизовано'}, status=401)
    print("Courier login for taken orders:", login)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT order_id, 
                   (customer_name).surname, (customer_name).firstname, (customer_name).middlename,
                   phone_number, 
                   (delivery_address).city, (delivery_address).street, (delivery_address).house, (delivery_address).flat
            FROM orders_taken_by_courier(%s)
        """, [login])
        rows = cursor.fetchall()
    data = [
        {
            'order_id': row[0],
            'surname': row[1],
            'firstname': row[2],
            'middlename': row[3],
            'phone': row[4],
            'city': row[5],
            'street': row[6],
            'house': row[7],
            'flat': row[8]
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def update_order_status(request):
    try:
        data = json.loads(request.body)
        order_id = data.get("order_id")
        status = data.get("status")
        if not order_id or not status:
            return HttpResponseBadRequest("Не вказано замовлення або статус")
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Orders SET order_status = %s WHERE o_kod = %s",
                [status, order_id]
            )
        return JsonResponse({"success": True})
    except Exception as e:
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type="application/json")