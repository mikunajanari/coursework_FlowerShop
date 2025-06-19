from django.http import JsonResponse
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
        return JsonResponse({'error': str(e)}, status=400)

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
        return JsonResponse({'error': str(e)}, status=400)

@require_GET
def expenses_report(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    expense_type = request.GET.get("type")
    if not start or not end or not expense_type:
        return JsonResponse({"error": "Не всі параметри"}, status=400)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT expense_type, item_name, amount, price, total, date
            FROM Expenses_View
            WHERE date BETWEEN %s AND %s AND expense_type = %s
            ORDER BY date DESC
        """, [start, end, 'добрива' if expense_type == 'fertilizers' else 'квіти'])
        rows = cursor.fetchall()
    data = [
        {
            'expense_type': row[0],
            'item_name': row[1],
            'amount': row[2],
            'price': float(row[3]),
            'total': float(row[4]),
            'date': str(row[5])
        }
        for row in rows
    ]
    total_sum = sum(row['total'] for row in data)
    return JsonResponse({"data": data, "total_sum": total_sum})

@require_GET
def income_report(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    if not start or not end:
        return JsonResponse({"error": "Не всі параметри"}, status=400)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT out_species_name, out_genus_name, out_sold_amount, out_total_earned, out_total_expenses, out_profit
            FROM get_revenue_report_with_totals(%s, %s)
        """, [start, end])
        rows = cursor.fetchall()
    data = [
        {
            'species_name': row[0],
            'genus_name': row[1],
            'sold_amount': row[2],
            'total_earned': float(row[3]) if row[3] is not None else None,
            'total_expenses': float(row[4]) if row[4] is not None else None,
            'profit': float(row[5]) if row[5] is not None else None,
        }
        for row in rows
    ]
    return JsonResponse(data, safe=False)