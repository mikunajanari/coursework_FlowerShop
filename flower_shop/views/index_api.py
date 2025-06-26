from django.db import connection
from django.shortcuts import render

def index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_user;")
        current_user = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM get_most_popular_species();")
        rows = cursor.fetchall()
    popular_products = [
        {
            'species_id': row[0],
            'species_name': row[1],
            'genus_name': row[2],
            'photo_link': row[3],
        }
        for row in rows
    ]
    return render(
        request,
        "flower_shop/index.html",
        {"popular_products": popular_products, "current_user": current_user}
    )