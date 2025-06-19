from django.shortcuts import render

def home(request):
    return render(request, 'flower_shop/index.html')

def about(request):
    return render(request, 'flower_shop/about.html')

def login(request):
    return render(request, 'flower_shop/login.html')

def signup(request):
    return render(request, 'flower_shop/signup.html')

def cart(request):
    return render(request, 'flower_shop/cart.html')

def checkout(request):
    return render(request, 'flower_shop/checkout.html')

def confirmation(request):
    return render(request, 'flower_shop/confirmation.html')

def profile_details(request):
    return render(request, 'flower_shop/profile_details.html')

def client_orders(request):
    return render(request, 'flower_shop/client_orders.html')

def shop(request):
    return render(request, 'flower_shop/shop.html')

def product_single(request):
    return render(request, 'flower_shop/product_single.html')

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