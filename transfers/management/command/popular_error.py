from django.core.management.base import BaseCommand
from transfers.models import Error

ERRORS =[
        32700, "Ext id must be unique", "Ext id должен быть уникальным", "Ext id noyob bo'lishi kerak",
        32701, "Ext id already exists", "Ext id уже существует", "Ext id allaqancha mavjud",
        32702, "Balance is not enough", "Недостаточно средств", "Hisobda mablag‘ yetarli emas",
        32703, "SMS service is not bind", "SMS сервис не подключен", "SMS xizmati ulanmagan",
        32704, "Card expiry is not valid", "Срок действия карты недействителен", "Karta amal qilish muddati noto‘g‘ri",
        32705, "Card is not active", "Карта не активна", "Karta faol emas"
        ]

class Command(BaseCommand):
    help = "Populate Error table with predefined messages"

    def handle(self, *args, **kwargs):
        for code, en, ru, uz in ERRORS:
            obj, created = Error.objects.get_or_create(
                code=code,
                defaults={'en': en, 'ru': ru, 'uz': uz}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Inserted error {code}"))
            else:
                self.stdout.write(self.style.WARNING(f"Error {code} already exists"))


