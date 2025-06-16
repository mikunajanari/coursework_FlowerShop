from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.db import connection
import json
from ..models import Species

def greenhouse(request):
    return render(request, 'flower_shop/greenhouse_dashboard.html')

@csrf_exempt
def plant_flowers_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        species_id = data.get('speciesId')
        quantity = data.get('amount')
        if not species_id or not quantity:
            return HttpResponseBadRequest("Missing parameters")

        with connection.cursor() as cursor:
            cursor.execute("SELECT plant_flowers(%s, %s)", [species_id, quantity])
        return JsonResponse({'status': 'ok'})

@csrf_exempt
def mark_ready_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        planted_id = data.get('plantedId')
        if not planted_id:
            return HttpResponseBadRequest("Missing plantedId")

        with connection.cursor() as cursor:
            cursor.execute("SELECT mark_ready_for_sale(%s)", [planted_id])
        return JsonResponse({'status': 'ok'})

@csrf_exempt
def write_off_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        planted_id = data.get('plantedId')
        quantity = data.get('amount')
        if not planted_id or not quantity:
            return HttpResponseBadRequest("Missing parameters")

        with connection.cursor() as cursor:
            cursor.execute("SELECT write_off_flowers(%s, %s)", [planted_id, quantity])
        return JsonResponse({'status': 'ok'})

@csrf_exempt
def use_fertilizer_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fert_id = data.get('fertilizerId')
        amount = data.get('amount')
        if not fert_id or not amount:
            return HttpResponseBadRequest("Missing parameters")

        with connection.cursor() as cursor:
            cursor.execute("SELECT use_fertilizer(%s, %s)", [fert_id, amount])
        return JsonResponse({'status': 'ok'})
    
@require_GET
def list_species(request):
    species = Species.objects.select_related('genus').all()
    data = [{
        'id': s.s_kod,
        'name': s.species_name,
        'genus': s.genus.genus_name
    } for s in species]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def plant_flowers(request):
    try:
        data = json.loads(request.body)
        species_id = data['species_id']
        quantity = data['quantity']
        with connection.cursor() as cursor:
            cursor.execute("SELECT plant_flowers(%s, %s)", [species_id, quantity])
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_GET
def list_unready_plants(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT p.p_kod, g.genus_name, s.species_name, p.amount, p.planting_day
            FROM Planted p
            JOIN Species s ON p.flower = s.s_kod
            JOIN Genera g ON s.genus = g.g_kod
            WHERE NOT EXISTS (
                SELECT 1 FROM Product pr WHERE pr.flower = p.p_kod
            )
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

@csrf_exempt
@require_POST
def mark_ready(request):
    try:
        data = json.loads(request.body)
        planted_id = data['planted_id']
        with connection.cursor() as cursor:
            cursor.execute("SELECT mark_ready_for_sale(%s)", [planted_id])
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@require_GET
def list_available_for_writeoff(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT p.p_kod, g.genus_name, s.species_name, p.amount, p.planting_day
            FROM Planted p
            JOIN Species s ON p.flower = s.s_kod
            JOIN Genera g ON s.genus = g.g_kod
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

@csrf_exempt
@require_POST
def write_off(request):
    try:
        data = json.loads(request.body)
        planted_id = data['planted_id']
        quantity = data['quantity']
        with connection.cursor() as cursor:
            cursor.execute("SELECT write_off_flowers(%s, %s)", [planted_id, quantity])
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    
@require_GET
def get_fertilizer_list(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT gf.kod, f.fertilizer_name, s.supplier_name
            FROM Genus_Fertilizer gf
            JOIN Fertilizers f ON gf.fertilizer = f.fe_kod
            JOIN Ordered_Fertilizers ofr ON f.fe_kod = ofr.fertilizer_id
            JOIN Suppliers s ON ofr.supplier_id = s.s_kod
            GROUP BY gf.kod, f.fertilizer_name, s.supplier_name
        ''')
        rows = cursor.fetchall()

    data = [
        {
            'id': row[0],
            'name': row[1],
            'supplier': row[2]
        } for row in rows
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
@require_POST
def use_fertilizer(request):
    try:
        data = json.loads(request.body)
        fertilizer_id = data['fertilizerId']
        amount = data['amount']

        with connection.cursor() as cursor:
            cursor.execute("SELECT use_fertilizer(%s, %s)", [fertilizer_id, amount])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponseBadRequest(str(e))

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
    
@require_GET
def get_grouped_fertilizers(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT gf.kod, gf.genus, f.fertilizer_name, s.supplier_name
            FROM Genus_Fertilizer gf
            JOIN Fertilizers f ON gf.fertilizer = f.fe_kod
            JOIN Ordered_Fertilizers ofr ON f.fe_kod = ofr.fertilizer_id
            JOIN Suppliers s ON ofr.supplier_id = s.s_kod
            GROUP BY gf.kod, gf.genus, f.fertilizer_name, s.supplier_name
        ''')
        rows = cursor.fetchall()

    result = {}
    for row in rows:
        genus_id = row[1]
        fert = {'id': row[0], 'name': row[2], 'supplier': row[3]}
        result.setdefault(genus_id, []).append(fert)

    return JsonResponse(result)