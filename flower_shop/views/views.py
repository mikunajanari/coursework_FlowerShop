from django.shortcuts import render
from django.shortcuts import redirect
from django.db import connection

def index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_user;")
        current_user = cursor.fetchone()[0]
    print("Postgres current_user:", current_user)
    return render(request, "flower_shop/index.html", {"current_user": current_user})

def about(request):
    return render(request, 'flower_shop/about.html')

def cart(request):
    return render(request, 'flower_shop/cart.html')

def courier(request):
    groups = request.session.get('pg_groups', [])
    if 'courier' not in groups:
        return redirect('login')
    return render(request, 'flower_shop/courier_dashboard.html')

def admin(request):
    groups = request.session.get('pg_groups', [])
    if 'administrator' not in groups:
        return redirect('login')
    return render(request, 'flower_shop/admin_dashboard.html')

def greenhouse(request):
    groups = request.session.get('pg_groups', [])
    if 'greenhouseworker' not in groups:
        return redirect('login')
    return render(request, 'flower_shop/greenhouse_dashboard.html')

def accountant(request):
    groups = request.session.get('pg_groups', [])
    if 'accountant' not in groups:
        return redirect('login')
    return render(request, 'flower_shop/accountant_dashboard.html')

def manager(request):
    groups = request.session.get('pg_groups', [])
    if 'salesmanager' not in groups:
        return redirect('login')
    return render(request, 'flower_shop/manager_dashboard.html')

def logout_view(request):
    request.session.flush()  # Очищає сесію
    return redirect('index')
