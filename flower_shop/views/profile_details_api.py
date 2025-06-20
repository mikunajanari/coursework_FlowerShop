from django.shortcuts import render, redirect
from django.db import connection

def profile_details(request):
    # Отримати поточні дані клієнта
    customer = None
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT (cust_name).FirstName, (cust_name_.Surname, (cust_name)(.MiddleName,
                   phone_number, email,
                   (address).City, (address).Street, (address).House, (address).Flat
            FROM Customers
            WHERE REPLACE(email, '@', '_') = SESSION_USER
        """)
        row = cursor.fetchone()
        if row:
            customer = {
                "first_name": row[0],
                "surname": row[1],
                "middle_name": row[2],
                "phone": row[3],
                "email": row[4],
                "city": row[5],
                "street": row[6],
                "house": row[7],
                "flat": row[8],
            }

    if request.method == "POST":
        data = request.POST
        # Оновлення кожного поля окремо, якщо воно змінене
        with connection.cursor() as cursor:
            if data.get("first_name") and data.get("first_name") != customer["first_name"]:
                cursor.execute("SELECT update_customer_first_name(%s)", [data.get("first_name")])
            if data.get("surname") and data.get("surname") != customer["surname"]:
                cursor.execute("SELECT update_customer_surname(%s)", [data.get("surname")])
            if data.get("middle_name") and data.get("middle_name") != customer["middle_name"]:
                cursor.execute("SELECT update_customer_middle_name(%s)", [data.get("middle_name")])
            if data.get("phone") and data.get("phone") != customer["phone"]:
                cursor.execute("SELECT update_customer_phone(%s)", [data.get("phone")])
            if data.get("city") and data.get("city") != customer["city"]:
                cursor.execute("SELECT update_customer_city(%s)", [data.get("city")])
            if data.get("street") and data.get("street") != customer["street"]:
                cursor.execute("SELECT update_customer_street(%s)", [data.get("street")])
            if data.get("house") and str(data.get("house")) != str(customer["house"]):
                cursor.execute("SELECT update_customer_house(%s)", [data.get("house")])
            if data.get("flat") and str(data.get("flat")) != str(customer["flat"]):
                cursor.execute("SELECT update_customer_flat(%s)", [data.get("flat")])
            if data.get("password"):
                cursor.execute("SELECT change_customer_password(%s)", [data.get("password")])
        return redirect("profile_details")

    return render(request, "flower_shop/profile_details.html", {"customer": customer})