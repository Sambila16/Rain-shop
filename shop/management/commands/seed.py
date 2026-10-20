from django.core.management.base import BaseCommand
from shop.models import Category

class Command(BaseCommand):
    help = 'Create the starting product categories'
    def handle(self, *a, **k):
        for n in ['Water', 'Soft Drinks', 'Juices', 'Sweets and Candy', 'Biscuits and Snacks', 'Others']:
            Category.objects.get_or_create(name=n)
        self.stdout.write('Categories ready.')
