from django.core.management.base import BaseCommand

from apps.customers.models import Customer

class Command(BaseCommand):
    help = "Eliminar todos los registros de asociados"

        
    def handle(self, *args, **options):
        Customer.objects.all().delete()