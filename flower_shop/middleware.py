from django.conf import settings
from django.db import connections

class DynamicDBUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Не підміняємо користувача для сторінки логіну та статичних файлів
        if request.path.startswith('/login') or request.path.startswith('/static'):
            return self.get_response(request)

        pg_user = request.session.get('pg_user')
        pg_password = request.session.get('pg_password')
        if pg_user and pg_password:
            settings.DATABASES['default']['USER'] = pg_user
            settings.DATABASES['default']['PASSWORD'] = pg_password
            connections['default'].close()
        response = self.get_response(request)
        return response