from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.signals import post_save, pre_delete
from django.db import connection
from django.conf import settings

from . import models


admin.site.register(models.Tenant)


@admin.register(models.TenantUser)
class TenantUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('tenant', 'instrument')}),
    ) + UserAdmin.fieldsets
    add_fieldsets = (
        (None, {'fields': ('tenant', 'instrument')}),
    ) + UserAdmin.add_fieldsets
    list_display = UserAdmin.list_display + ('tenant', 'instrument')
    list_filter = UserAdmin.list_display + ('tenant', 'instrument')


# Register your models here.
# create db role for RLS control. see: https://scrapbox.io/shimizukawa/Django_PG_RLS
def on_create_tenant(sender, instance, created, **kwargs):
    if created:
        tenant_id = instance.tenant_id

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT rolname FROM pg_roles WHERE rolname = '{tenant_id}'")
            role = cursor.fetchone()

            if role:
                print(f"Role '{tenant_id}' already exists.")
            else:
                print(f"Role '{tenant_id}' has been created.")
                cursor.execute(f'CREATE ROLE "{tenant_id}"')
                cursor.execute(f'GRANT {settings.RLS_ROLE_NAME} TO "{tenant_id}"')
                cursor.execute(f'GRANT "{tenant_id}" TO "{settings.RLS_ADMIN_ROLE_NAME}"')


post_save.connect(on_create_tenant, sender=models.Tenant)


def on_delete_tenant(sender, instance, using, **kwargs):
    """削除時にはROLEも削除しておく"""
    tenant_id = instance.tenant_id
    with connection.cursor() as cursor:
        cursor.execute(f'REVOKE {settings.RLS_ROLE_NAME} FROM "{tenant_id}"')
        cursor.execute(f'DROP ROLE "{tenant_id}"')


pre_delete.connect(on_delete_tenant, sender=models.Tenant)