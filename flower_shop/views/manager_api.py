from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import connection
import json

@csrf_exempt
@require_POST
def create_client(request):
    import json
    try:
        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT create_customer(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    data['first_name'],
                    data['surname'],
                    data['middle_name'],
                    data['phone'],
                    data['email'],
                    data['city'],
                    data['street'],
                    data['house'],
                    data['flat'],
                    None,  # photo
                    data['db_password']
                ]
            )
            new_id = cursor.fetchone()[0]
        return JsonResponse({'id': new_id})
    except Exception as e:
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type="application/json")

@require_GET
def list_clients(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kod, (cust_name).surname, (cust_name).firstname, (cust_name).middlename, email
            FROM Customers
            WHERE kod <> 0
        """)
        rows = cursor.fetchall()
    data = [
        {'id': row[0], 'surname': row[1], 'first_name': row[2], 'middle_name': row[3], 'email': row[4]}
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def list_flowers(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT s_kod, genus_name, species_name FROM Species JOIN Genera ON genus = g_kod")
        rows = cursor.fetchall()
    data = [
        {'id': row[0], 'genus': row[1], 'species': row[2]}
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def create_order_with_items_api(request):
    import json
    try:
        data = json.loads(request.body)
        customer_id = data['customer_id']
        delivery_date = data['delivery_date']
        delivery_method = data['delivery_method']
        items = data['items']
        flower_orders = '{' + ','.join([f'"({item["flower_id"]},{item["amount"]})"' for item in items]) + '}'
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT create_order_with_items(%s::integer, %s::date, %s::varchar, VARIADIC %s::flower_order[])",
                [customer_id, delivery_date, delivery_method, flower_orders]
        )
            order_id = cursor.fetchone()[0]
        return JsonResponse({'order_id': order_id})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type="application/json")
    
@require_GET
def check_stock(request):
    species_id = request.GET.get("species_id")
    if not species_id:
        return HttpResponseBadRequest(json.dumps({'error': 'Не вказано вид квітки'}), content_type="application/json")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT species_id, genus_name, species_name, available_quantity
            FROM available_species
            WHERE species_id = %s
        """, [species_id])
        row = cursor.fetchone()
    if not row:
        return JsonResponse({'error': 'Квітку не знайдено'}, status=404)
    return JsonResponse({
        'species_id': row[0],
        'genus': row[1],
        'species': row[2],
        'available_quantity': row[3]
    })

@require_GET
def list_orders_by_client(request):
    client_id = request.GET.get("client_id")
    if not client_id:
        return HttpResponseBadRequest(json.dumps({'error': 'Не вказано клієнта'}), content_type="application/json")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT o_kod, delivery_date, order_status
            FROM Orders
            WHERE customer = %s
            ORDER BY delivery_date DESC
        """, [client_id])
        rows = cursor.fetchall()
    data = [
        {'order_id': row[0], 'delivery_date': row[1].strftime('%Y-%m-%d'), 'status': row[2]}
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def track_order(request):
    order_id = request.GET.get("order_id")
    if not order_id:
        return HttpResponseBadRequest("Не вказано номер замовлення")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT o_kod, order_status
            FROM Orders
            WHERE o_kod = %s
        """, [order_id])
        row = cursor.fetchone()
    if not row:
        return JsonResponse({'error': 'Замовлення не знайдено'}, status=404)
    return JsonResponse({'order_id': row[0], 'status': row[1]})
