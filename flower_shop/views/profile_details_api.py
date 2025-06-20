from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import default_storage
from django.conf import settings

def profile_details(request):
    # Отримати поточні дані клієнта
    customer = None
    user_login = request.user.username if request.user.is_authenticated else request.session.get('pg_user')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM get_profile_by_login(%s)", [user_login])
        row = cursor.fetchone()
        if row:
            customer = {
                "first_name": row[0],
                "surname": row[1],
                "middle_name": row[2],
                "phone": row[3],
                "email": row[4],
                "photo_link": row[5],
                "city": row[6],
                "street": row[7],
                "house": row[8],
                "flat": row[9],
            }

    # Завантаження нового фото
    if request.method == "POST":
        with connection.cursor() as cursor:
            if "change_photo" in request.POST:
                photo = request.FILES.get("photo")
                if photo:
                    filename = default_storage.save(f"profile_photos/{request.session['pg_user']}_{photo.name}", photo)
                    photo_url = f"/media/{filename}"
                    cursor.execute("SELECT update_customer_photo(%s)", [photo_url])
                return redirect("profile_details")
            if "update_first_name" in request.POST:
                cursor.execute("SELECT update_customer_first_name(%s)", [request.POST.get("first_name")])
                return redirect("profile_details")
            if "update_surname" in request.POST:
                cursor.execute("SELECT update_customer_surname(%s)", [request.POST.get("surname")])
                return redirect("profile_details")
            if "update_middle_name" in request.POST:
                cursor.execute("SELECT update_customer_middle_name(%s)", [request.POST.get("middle_name")])
                return redirect("profile_details")
            if "update_phone" in request.POST:
                cursor.execute("SELECT update_customer_phone(%s)", [request.POST.get("phone")])
                return redirect("profile_details")
            if "update_city" in request.POST:
                cursor.execute("SELECT update_customer_city(%s)", [request.POST.get("city")])
                return redirect("profile_details")
            if "update_street" in request.POST:
                cursor.execute("SELECT update_customer_street(%s)", [request.POST.get("street")])
                return redirect("profile_details")
            if "update_house" in request.POST:
                cursor.execute("SELECT update_customer_house(%s)", [request.POST.get("house")])
                return redirect("profile_details")
            if "update_flat" in request.POST:
                cursor.execute("SELECT update_customer_flat(%s)", [request.POST.get("flat")])
                return redirect("profile_details")
            if "update_password" in request.POST:
                cursor.execute("SELECT change_customer_password(%s)", [request.POST.get("password")])
                return redirect("profile_details")

    return render(request, "flower_shop/profile_details.html", {"customer": customer})