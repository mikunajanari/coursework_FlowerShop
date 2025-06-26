from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import default_storage
from django.conf import settings
import psycopg2
from django.contrib import messages

def profile_details(request):
    if not request.session.get('pg_user'):
        return redirect('login')
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
                    filename = default_storage.save(f"profile_photos/{user_login}_{photo.name}", photo)
                    photo_url = f"/media/{filename}"
                    cursor.execute("SELECT update_customer_field_internal(%s, %s)", ['photo_link', photo_url])
                return redirect("profile_details")
            if "update_first_name" in request.POST:
                cursor.execute("SELECT update_customer_name_field(%s, %s)", ['FirstName', request.POST.get("first_name")])
                return redirect("profile_details")
            if "update_surname" in request.POST:
                cursor.execute("SELECT update_customer_name_field(%s, %s)", ['Surname', request.POST.get("surname")])
                return redirect("profile_details")
            if "update_middle_name" in request.POST:
                cursor.execute("SELECT update_customer_name_field(%s, %s)", ['MiddleName', request.POST.get("middle_name")])
                return redirect("profile_details")
            if "update_phone" in request.POST:
                cursor.execute("SELECT update_customer_field_internal(%s, %s)", ['phone_number', request.POST.get("phone")])
                return redirect("profile_details")
            if "update_city" in request.POST:
                cursor.execute("SELECT update_customer_address_field(%s, %s)", ['City', request.POST.get("city")])
                return redirect("profile_details")
            if "update_street" in request.POST:
                cursor.execute("SELECT update_customer_address_field(%s, %s)", ['Street', request.POST.get("street")])
                return redirect("profile_details")
            if "update_house" in request.POST:
                cursor.execute("SELECT update_customer_address_field(%s, %s)", ['House', request.POST.get("house")])
                return redirect("profile_details")
            if "update_flat" in request.POST:
                cursor.execute("SELECT update_customer_address_field(%s, %s)", ['Flat', request.POST.get("flat")])
                return redirect("profile_details")
            if "update_password" in request.POST:
                old_password = request.POST.get("old_password")
                new_password = request.POST.get("password")
                user_login = request.user.username if request.user.is_authenticated else request.session.get('pg_user')

                if check_pg_password(user_login, old_password):
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT change_customer_password(%s)", [new_password])
                    messages.success(request, "Пароль успішно змінено. Увійдіть знову.")
                    request.session.flush()
                    return redirect("profile_details")
                else:
                    messages.error(request, "Старий пароль невірний.")
                return redirect("profile_details")
    
    return render(request, "flower_shop/profile_details.html", {"customer": customer})

def check_pg_password(username, password):
    db_settings = connection.settings_dict
    try:
        conn = psycopg2.connect(
            dbname=db_settings['NAME'],
            user=username,
            password=password,
            host=db_settings.get('HOST', ''),
            port=db_settings.get('PORT', ''),
        )
        conn.close()
        return True
    except Exception:
        return False