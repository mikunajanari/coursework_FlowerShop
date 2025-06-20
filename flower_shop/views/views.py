from django.shortcuts import render
from django.shortcuts import redirect
from django.db import connection

def index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_user;")
        current_user = cursor.fetchone()[0]
    print("Postgres current_user:", current_user)  # побачите у консолі Django
    return render(request, "flower_shop/index.html", {"current_user": current_user})

def about(request):
    return render(request, 'flower_shop/about.html')

def cart(request):
    return render(request, 'flower_shop/cart.html')

def client_orders(request):
    return render(request, 'flower_shop/client_orders.html')

def courier(request):
    return render(request, 'flower_shop/courier_dashboard.html')

def admin(request):
    return render(request, 'flower_shop/admin_dashboard.html')

def greenhouse(request):
    return render(request, 'flower_shop/greenhouse_dashboard.html')

def accountant(request):
    return render(request, 'flower_shop/accountant_dashboard.html')

def manager(request):
    return render(request, 'flower_shop/manager_dashboard.html')

def logout_view(request):
    request.session.flush()  # Очищає сесію
    return redirect('index')
