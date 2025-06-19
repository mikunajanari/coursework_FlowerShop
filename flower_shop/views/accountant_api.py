from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.db import connection
import json

@require_GET
def list_fertilizers(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT fe_kod, fertilizer_name FROM Fertilizers")
        rows = cursor.fetchall()
    data = [{'id': row[0], 'name': row[1]} for row in rows]
    return JsonResponse(data, safe=False)

@require_GET
def list_suppliers(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT s_kod, supplier_name FROM Suppliers")
        rows = cursor.fetchall()
    data = [{'id': row[0], 'name': row[1]} for row in rows]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def order_fertilizer_api(request):
    try:
        data = json.loads(request.body)
        fertilizer_id = data['fertilizer_id']
        supplier_id = data['supplier_id']
        amount = data['amount']
        price = data['price']
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT order_fertilizer(%s, %s, %s, %s)",
                [fertilizer_id, supplier_id, amount, price]
            )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_GET
def list_ready_products(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT product_id, genus_name, species_name, planting_day FROM ready_products_view ORDER BY product_id DESC')
        rows = cursor.fetchall()
    data = [
        {
            'id': row[0],
            'genus': row[1],
            'species': row[2],
            'planting_day': row[3] if isinstance(row[3], str) else row[3].strftime('%Y-%m-%d')
        } for row in rows
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def set_flower_price_api(request):
    import json
    try:
        data = json.loads(request.body)
        product_id = data['flowerId']
        price = data['price']
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT set_flower_price(%s, %s)",
                [product_id, price]
            )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))