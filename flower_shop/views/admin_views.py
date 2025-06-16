from django.db import connection
from django.shortcuts import render, redirect
from ..models import Genera, Fertilizers, Suppliers

def admin(request):
    return render(request, 'flower_shop/admin_dashboard.html')

def add_genus(request):
    if request.method == 'POST':
        name = request.POST.get('genus_name')
        if name:
            Genera.objects.create(genus_name=name)
    return redirect('admin_dashboard')

def add_species_sql(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SELECT add_species(%s, %s, %s, %s, %s)", [
                request.POST['species_name'],
                request.POST['genus_id'],
                request.POST['instruction'],
                request.POST['storage_period'],
                request.POST.get('photo_link') or None
            ])
    return redirect('admin_dashboard')

def add_fertilizer(request):
    if request.method == 'POST':
        name = request.POST.get('fertilizer_name')
        if name:
            Fertilizers.objects.create(fertilizer_name=name)
    return redirect('admin_dashboard')

def link_genus_fertilizer_sql(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SELECT link_genus_fertilizer(%s, %s)", [
                request.POST['genus_id'],
                request.POST['fertilizer_id']
            ])
    return redirect('admin_dashboard')

def add_supplier(request):
    if request.method == 'POST':
        supplier_name = request.POST['supplier_name']
        address = request.POST['address']
        phone = request.POST['phone']
        Suppliers.objects.create(
            supplier_name=supplier_name,
            address=address,
            phone_number=phone
        )
    return redirect('admin_dashboard')

def add_courier_sql(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SELECT create_courier(%s, %s, %s, %s, %s, %s)", [
                request.POST['first_name'],
                request.POST['surname'],
                request.POST.get('middle_name') or '',
                request.POST['phone'],
                request.POST['email'],
                request.POST.get('password') or None
            ])
    return redirect('admin_dashboard')