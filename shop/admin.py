from django.contrib import admin
from .models import Category, Unit, Product, Customer, Sale
for m in (Category, Unit, Product, Customer, Sale): admin.site.register(m)
