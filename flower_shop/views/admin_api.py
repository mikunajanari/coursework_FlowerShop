"""
А1	Додавання нових родів квітів.	Назва роду.
А2	Додавання нових видів квітів.	Назва квітки, рід, інструкція (текст), період зберігання, зображення.
А3	Додавання нових добрив.	Назва добрива.
А4	Зв’язування родів із дозволеними добривами.	Сорт та дозволене добриво.
А5	Додавання нових постачальників.	Назва, адреса, телефон.
А6	Додавання нового кур’єра.	ПІБ кур’єра, контактні дані (телефон, email).
"""
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
import json

@csrf_exempt
def add_genus(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        genus_name = data.get('genus_name')
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Genera (genus_name) VALUES (%s)", [genus_name])
        return JsonResponse({'message': 'Рід додано!'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

def get_genera(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT genus_name FROM Genera ORDER BY genus_name")
        genera = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'genera': genera})

@csrf_exempt
def add_species_sql(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        species_name = data.get('species_name')
        genus_name = data.get('genus_name')
        instructions = data.get('instructions')
        storage_period = data.get('storage_period')
        photo_link = data.get('photo_link')
        with connection.cursor() as cursor:
            # Знайти id роду за назвою
            cursor.execute("SELECT g_kod FROM Genera WHERE genus_name = %s", [genus_name])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'error': 'Рід не знайдено!'}, status=400)
            genus_id = row[0]
            cursor.execute("SELECT add_species(%s, %s, %s, %s, %s)", [
                species_name, genus_id, instructions, storage_period, photo_link
            ])
        return JsonResponse({'message': 'Вид додано!'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def add_fertilizer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fertilizer_name = data.get('fertilizer_name')
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Fertilizer (fertilizer_name) VALUES (%s)", [fertilizer_name])
        return JsonResponse({'message': 'Добриво додано!'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def link_genus_fertilizer_sql(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        genus_id = data.get('genus_id')
        fertilizer_id = data.get('fertilizer_id')
        with connection.cursor() as cursor:
            cursor.execute("SELECT link_genus_fertilizer(%s, %s)", [genus_id, fertilizer_id])
        return JsonResponse({'message': 'Звʼязок додано!'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def add_supplier(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        supplier_name = data.get('supplier_name')
        address = data.get('address')
        phone = data.get('phone')
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Supplier (supplier_name, address, phone) VALUES (%s, %s, %s)",
                [supplier_name, address, phone]
            )
        return JsonResponse({'message': 'Постачальника додано!'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def add_courier_sql(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        first_name = data.get('first_name')
        surname = data.get('surname')
        middle_name = data.get('middle_name')
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT create_courier(%s, %s, %s, %s, %s, %s)",
                [first_name, surname, middle_name, phone, email, password]
            )
        return JsonResponse({'message': 'Курʼєра додано!'})
    return JsonResponse({'error': 'Invalid method'}, status=405)