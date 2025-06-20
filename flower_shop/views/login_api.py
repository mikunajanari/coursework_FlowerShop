from django.conf import settings
from django.shortcuts import render, redirect
from django.db.utils import OperationalError, ConnectionHandler

def login_pg(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        test_settings = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'FlowerSystem',
            'USER': username,
            'PASSWORD': password,
            'HOST': 'localhost',
            'PORT': '5432',
        }
        db_configs = {
            'default': settings.DATABASES['default'],
            'test': test_settings,
        }
        try:
            test_conn = ConnectionHandler(db_configs)['test']
            with test_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.rolname
                    FROM pg_roles r
                    JOIN pg_auth_members m ON r.oid = m.roleid
                    JOIN pg_roles u ON u.oid = m.member
                    WHERE u.rolname = current_user AND r.rolcanlogin = false;
                """)
                groups = [row[0] for row in cursor.fetchall()]
                print('groups:', groups)
            request.session['pg_user'] = username
            request.session['pg_password'] = password
            request.session['pg_groups'] = groups

            # Далі перевіряємо групу:
            if 'salesmanager' in groups:
                return redirect('manager_dashboard')
            elif 'accountant' in groups:
                return redirect('accountant_dashboard')
            elif 'greenhouseworker' in groups:
                return redirect('greenhouse_dashboard')
            elif 'administrator' in groups:
                return redirect('admin_dashboard')
            elif 'courier' in groups:
                return redirect('courier_dashboard')
            elif 'customer' in groups:
                return redirect('index')
            else:
                return redirect('index')  # Якщо група не знайдена, перенаправляємо на головну сторінку
        except OperationalError:
            error = "Невірний логін або пароль"
    return render(request, "flower_shop/login.html", {"error": error})