from django.shortcuts import render
from django.db import connection
from collections import defaultdict
from django.shortcuts import redirect
from django.contrib import messages

def client_orders(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_customer_history()")
        rows = cursor.fetchall()
    orders_grouped = defaultdict(list)
    for row in rows:
        order_id = row[0]
        orders_grouped[order_id].append({
            'order_id': row[0],
            'order_date': row[1],
            'delivery_date': row[2],
            'status': row[3],
            'species': row[4],
            'genus': row[5],
            'amount': row[6],
        })
    return render(request, "flower_shop/client_orders.html", {"orders_grouped": dict(orders_grouped)})

def cancel_order(request, order_id):
    if request.method == "POST":
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT cancel_order_by_current_user(%s)", [order_id])
                messages.success(request, f"Замовлення #{order_id} скасовано.")
            except Exception as e:
                messages.error(request, str(e))
    return redirect('client_orders')