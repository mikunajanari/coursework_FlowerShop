from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.db import connection
import json

@require_GET
def list_species(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT s.s_kod, s.species_name, g.genus_name, g.g_kod
            FROM Species s
            JOIN Genera g ON s.genus = g.g_kod
        ''')
        rows = cursor.fetchall()
    data = [
        {'id': row[0], 'name': row[1], 'genus': row[2], 'genus_id': row[3]}
        for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def list_unready_plants(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT p.p_kod, g.genus_name, s.species_name, p.amount, p.planting_day, s.storage_period
            FROM Planted p
            JOIN Species s ON p.flower = s.s_kod
            JOIN Genera g ON s.genus = g.g_kod
            WHERE NOT EXISTS (
                SELECT 1 FROM Product pr WHERE pr.flower = p.p_kod
            )
            AND (CURRENT_DATE <= p.planting_day + s.storage_period)
        ''')
        rows = cursor.fetchall()
    data = [
        {
            'id': row[0],
            'genus': row[1],
            'species': row[2],
            'amount': row[3],
            'planting_day': row[4].strftime('%Y-%m-%d')
        } for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def list_available_for_writeoff(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT p.p_kod, g.genus_name, s.species_name, p.amount, p.planting_day, s.storage_period
            FROM Planted p
            JOIN Species s ON p.flower = s.s_kod
            JOIN Genera g ON s.genus = g.g_kod
            WHERE (CURRENT_DATE <= p.planting_day + s.storage_period)
        ''')
        rows = cursor.fetchall()
    data = [
        {
            'id': row[0],
            'genus': row[1],
            'species': row[2],
            'amount': row[3],
            'planting_day': row[4].strftime('%Y-%m-%d')
        } for row in rows
    ]
    return JsonResponse(data, safe=False)

@require_GET
def get_grouped_fertilizers(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT gf.kod, gf.genus, f.fertilizer_name
            FROM Genus_Fertilizer gf
            JOIN Fertilizers f ON gf.fertilizer = f.fe_kod
        ''')
        rows = cursor.fetchall()
    result = {}
    for row in rows:
        genus_id = row[1]
        fert = {'id': row[0], 'name': row[2]}
        result.setdefault(genus_id, []).append(fert)
    return JsonResponse(result)

@csrf_exempt
@require_POST
def plant_with_fertilizer(request):
    try:
        data = json.loads(request.body)
        species_id = data['species_id']
        quantity = data['quantity']
        genus_fertilizer_id = data['genus_fertilizer_id']
        fertilizer_amount = data['fertilizer_amount']
        with connection.cursor() as cursor:
            cursor.execute("SELECT plant_flowers(%s, %s)", [species_id, quantity])
            cursor.execute("SELECT use_fertilizer(%s, %s)", [genus_fertilizer_id, fertilizer_amount])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@csrf_exempt
@require_POST
def mark_ready(request):
    try:
        data = json.loads(request.body)
        planted_id = data['planted_id']
        with connection.cursor() as cursor:
            cursor.execute("SELECT mark_ready_for_sale(%s)", [planted_id])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@csrf_exempt
@require_POST
def write_off(request):
    try:
        data = json.loads(request.body)
        planted_id = data['planted_id']
        quantity = data['quantity']
        with connection.cursor() as cursor:
            cursor.execute("SELECT write_off_flowers(%s, %s)", [planted_id, quantity])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))