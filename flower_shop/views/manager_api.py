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

@require_GET
def monthly_order_trends(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                month, delivered, total, total_trend, delivered_trend
            FROM Monthly_Order_Trends
            ORDER BY month
        """)
        rows = cursor.fetchall()
    data = [
        {
            'month': row[0].strftime('%Y-%m'),
            'delivered': row[1],
            'total': row[2],
            'total_trend': float(row[3]),
            'delivered_trend': float(row[4])
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def genus_ranking(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                genus_name,
                planted_rank,
                fertilizer_cost_rank,
                revenue_rank
            FROM GenusRanking
            ORDER BY planted_rank, genus_name
        """)
        rows = cursor.fetchall()
    data = [
        {
            'genus_name': row[0],
            'planted_rank': row[1],
            'fertilizer_cost_rank': row[2],
            'revenue_rank': row[3]
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def flower_demand(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    if not start or not end:
        return HttpResponseBadRequest("Не вказано період")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT species_id, species_name, genus_name, sold_amount, sold_percent
            FROM get_flower_demand(%s, %s)
            ORDER BY sold_amount DESC
        """, [start, end])
        rows = cursor.fetchall()
    data = [
        {
            'species_id': row[0],
            'species_name': row[1],
            'genus_name': row[2],
            'sold_amount': row[3],
            'sold_percent': float(row[4])
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def season_stats(request):
    year = request.GET.get("year")
    if not year:
        return HttpResponseBadRequest("Не вказано рік")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT season, species_name, genus_name, avg_sold, total_earned
            FROM get_seasonal_stats(%s)
            ORDER BY season, total_earned DESC
        """, [year])
        rows = cursor.fetchall()
    data = [
        {
            'season': row[0],
            'species_name': row[1],
            'genus_name': row[2],
            'avg_sold': float(row[3]),
            'total_earned': float(row[4])
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def client_preferences(request):
    client_id = request.GET.get("client_id")
    if not client_id:
        return HttpResponseBadRequest("Не вказано клієнта")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT species_name, genus_name, total_amount, order_dates, prices
            FROM get_customer_preferences(%s)
            ORDER BY total_amount DESC
        """, [client_id])
        rows = cursor.fetchall()
    data = [
        {
            'species_name': row[0],
            'genus_name': row[1],
            'total_amount': row[2],
            'order_dates': row[3],
            'prices': row[4]
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def courier_performance(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    if not start or not end:
        return HttpResponseBadRequest("Не вказано період")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT courier_id, full_name, delivered_percent, undelivered_percent
            FROM analyze_courier_performance(%s, %s)
            ORDER BY delivered_percent DESC NULLS LAST
        """, [start, end])
        rows = cursor.fetchall()
    data = [
        {
            'courier_id': row[0],
            'full_name': row[1],
            'delivered_percent': float(row[2]) if row[2] is not None else None,
            'undelivered_percent': float(row[3]) if row[3] is not None else None
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def most_popular_species(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT species_id, species_name, genus_name, total_amount
            FROM Most_Popular_Species_Per_Genus
            ORDER BY genus_name, species_name
        """)
        rows = cursor.fetchall()
    data = [
        {
            'species_id': row[0],
            'species_name': row[1],
            'genus_name': row[2],
            'total_amount': row[3]
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)