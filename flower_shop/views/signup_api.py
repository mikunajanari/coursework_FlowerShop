from django.shortcuts import render, redirect
from django.db import connection

def signup(request):
    if request.method == "POST":
        data = request.POST
        email = data.get("email")
        password = data.get("password")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT create_customer(
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                data.get("first_name"),
                data.get("surname"),
                data.get("middle_name"),
                data.get("phone"),
                email,
                data.get("city"),
                data.get("street"),
                data.get("house"),
                data.get("flat"),
                None,
                password,
            ])
        # Додаємо логін нового клієнта у сесію
        username = email.replace('@', '_')
        request.session['pg_user'] = username
        request.session['pg_password'] = password
        return redirect("index")
    return render(request, "flower_shop/signup.html")