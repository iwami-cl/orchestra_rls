from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from user.models import Tenant, TenantUser
from user.models import CustomPermission
from user.permission_settings import PERMISSION_SETTINGS
from django.contrib.auth.models import Permission

# コマンド
# python manage.py insert_custome_permissions
class Command(BaseCommand):

    help = 'カスタムパーミッションを挿入します'

    def handle(self, *args, **kwargs):
        for keyperm, perm in PERMISSION_SETTINGS.items():
            permission, created = CustomPermission.objects.get_or_create(
                permission=Permission.objects.get(codename=keyperm),
                # DjangoのPermissionモデルから対応するPermissionを取得して関連付け
                defaults={
                    'display_name': perm['display_name'],
                    'private': perm['private'],
                    'description': perm['description']
                }
            )
            # 既存のPermissionも強制的に更新する
            if created:
                self.stdout.write(self.style.SUCCESS(f"Permission '{perm['display_name']}' created successfully."))
            else:
                permission.display_name = perm['display_name']
                permission.private = perm['private']
                permission.description = perm['description']
                permission.save()  # 既存のPermissionを更新
                self.stdout.write(self.style.WARNING(f"Permission '{perm['display_name']}' already exists."))