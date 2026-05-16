from django.core.management.base import BaseCommand
import random
from instrument.models import Instrument
from user.models import Tenant, TenantUser

# コマンドの実行方法: python manage.py set_instrument
class Command(BaseCommand):
    help = '各テナントユーザーに楽器をランダムに割り当てます'
    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            print("No tenants found, skipping instrument assignment.")
            print("Please execute [python manage.py insert_tenant] and [python manage.py insert_instrument].")
            return
        for tenant in tenants:
            users = TenantUser.objects.filter(tenant=tenant)

            if not users.exists():
                print(f"No users found for tenant {tenant.name}, skipping.")
                print("Please execute [python manage.py insert_tenant] and [python manage.py insert_instrument].")
                continue
            instruments = Instrument.objects.filter(tenant=tenant)
            if not instruments.exists():
                print(f"No instruments found for tenant {tenant.name}, skipping.")
                print("Please execute [python manage.py insert_instrument].")
                continue

            for u in users:
                instrument = random.choice(instruments)
                u.instrument = instrument
                print(u.username + " -> " + instrument.name)
                u.save()