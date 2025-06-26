from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from flower_shop.models import Planted, DefectiveProduct

class Command(BaseCommand):
    help = 'Списує посаджені квіти, у яких закінчився термін придатності виду'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        count = 0
        # Знаходимо всі посаджені квіти, у яких закінчився термін придатності
        for planted in Planted.objects.filter(amount__gt=0):
            expire_date = planted.planting_day + timezone.timedelta(days=planted.flower.storage_period * 30)
            if expire_date < today:
                already_written_off = DefectiveProduct.objects.filter(flower=planted).aggregate(total=models.Sum('amount'))['total'] or 0
                to_writeoff = planted.amount - already_written_off
                if to_writeoff > 0:
                    DefectiveProduct.objects.create(
                        flower=planted,
                        amount=to_writeoff
                    )
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'Списано {count} посаджених квітів'))