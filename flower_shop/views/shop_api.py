from django.shortcuts import render
from django.db import connection

def shop(request):
    sort = request.GET.get('sort', 'asc')
    genus = request.GET.get('genus', '')

    query = """
        SELECT product_id, species_name, genus_name, price, photo_link, available_amount
        FROM Available_Products_For_Guests
    """
    params = []
    if genus:
        query += " WHERE genus_name = %s"
        params.append(genus)
    if sort == 'desc':
        query += " ORDER BY price DESC"
    else:
        query += " ORDER BY price ASC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        products = [
            {
                'id': row[0],
                'species_name': row[1],
                'genus_name': row[2],
                'price': row[3],
                'photo_link': row[4],
                'available_amount': row[5],
            }
            for row in cursor.fetchall()
        ]

    # Для фільтрації — список унікальних родів
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT genus_name FROM Available_Products_For_Guests ORDER BY genus_name")
        genera = [row[0] for row in cursor.fetchall()]

    return render(request, "flower_shop/shop.html", {
        "products": products,
        "genera": genera,
        "current_genus": genus,
        "current_sort": sort,
    })

def product_single(request, product_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT product_id, species_name, genus_name, price, photo_link, available_amount, instruction
            FROM Available_Products_For_Guests
            WHERE product_id = %s
        """, [product_id])
        row = cursor.fetchone()
        if not row:
            return render(request, "flower_shop/product_not_found.html", status=404)
        product = {
            'id': row[0],
            'species_name': row[1],
            'genus_name': row[2],
            'price': row[3],
            'photo_link': row[4],
            'available_amount': row[5],
            'care_instructions': row[6],
        }
    return render(request, "flower_shop/product_single.html", {"product": product})