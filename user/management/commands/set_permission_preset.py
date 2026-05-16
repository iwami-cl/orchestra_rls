from django.core.management.base import BaseCommand

from user.models import Tenant
from user.models import CustomPermission, PermissionPreset
from user.permission_settings import DEFAULT_PERMISSION_PRESETS

# コマンド
# python manage.py set_permission_preset
class Command(BaseCommand):

    help = 'パーミッションプリセットを設定します'

    def handle(self, *args, **kwargs):
        # デフォルトのパーミッションが未設定のテナントに対して処理する
        for tenant in Tenant.objects.all():

            for preset in DEFAULT_PERMISSION_PRESETS:
                preset_obj, created = PermissionPreset.objects.get_or_create(
                    tenant=tenant,
                    name=preset['name']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Permission preset '{preset['name']}' created successfully for tenant '{tenant.name}'."))
                else:
                    self.stdout.write(self.style.WARNING(f"Permission preset '{preset['name']}' already exists for tenant '{tenant.name}'."))
                    # 既存のプリセットのパーミッションをいったんクリアしてから再設定する
                    preset_obj.permissions.clear()

                # パーミッションを関連付ける
                for perm_codename in preset['permissions']:
                    try:
                        custom_perm = CustomPermission.objects.get(permission__codename=perm_codename)
                        preset_obj.permissions.add(custom_perm)
                    except CustomPermission.DoesNotExist:
                        continue
                
                preset_obj.save()
