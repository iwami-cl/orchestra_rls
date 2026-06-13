from django.contrib import admin

from stripe.models import Price, Product

# Register your models here.
admin.site.register(Product)
admin.site.register(Price)
    