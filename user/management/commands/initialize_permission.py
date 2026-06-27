from django.core.management.base import BaseCommand

from user.models import Tenant, TenantUser
from user.models import CustomPermission, PermissionPreset
from user.permission_settings import DEFAULT_PERMISSION_PRESETS

# コマンド
# python manage.py initialize_permission --realm=<realm名> --preset_name=<プリセット名> --username=<任意>
class Command(BaseCommand):

    help = 'ユーザーにパーミッションを設定します(引数：realm, preset_name, username(任意))'

    def add_arguments(self, parser):
        parser.add_argument('--realm', type=str, help='テナントのrealmを指定してください')
        parser.add_argument('--preset_name', type=str, help='パーミッションプリセット名を指定してください')
        parser.add_argument('--username', type=str, help='特定のユーザーにのみ設定する場合はusernameを指定してください(任意)')

    def handle(self, *args, **kwargs):
        # 引数からテナントのrealmを取得
        realm = kwargs.get('realm')

        # 引数からパーミッションのプリセット名を取得
        preset_name = kwargs.get('preset_name')

        # 引数からユーザーのusernameを取得（任意）
        username = kwargs.get('username')

        # 引数チェック
        if not realm or not preset_name:
            self.stdout.write(self.style.ERROR("テナントのrealmとパーミッションプリセット名を指定してください。"))
            return
        
        try:
            tenant = Tenant.objects.get(realm=realm)
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"指定されたテナントのrealm '{realm}' は存在しません。"))
            return
        
        try:
            preset = PermissionPreset.objects.get(tenant=tenant, name=preset_name)
        except PermissionPreset.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"指定されたパーミッションプリセット '{preset_name}' は存在しません。"))
            return
        
        # パーミッションプリセットが見つかった場合の処理
        self.stdout.write(self.style.SUCCESS(f"パーミッションプリセット '{preset_name}' が見つかりました。"))

        # 特定のユーザーにのみ設定する場合
        if username:
            try:
                once_user = TenantUser.objects.get(tenant=tenant, username=username)
                # once_user.user_permissions.clear()

                # プリセットのパーミッションをユーザーに追加
                for perm in preset.permissions.all():
                    once_user.user_permissions.add(perm.permission)
                once_user.save()
                self.stdout.write(self.style.SUCCESS(f"ユーザー '{once_user.username}' にパーミッションを設定しました。"))
            except TenantUser.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"指定されたユーザー '{username}' は存在しません。"))
                return
        else:
            users = TenantUser.objects.filter(tenant=tenant)

            for user in users:
                # 既存のパーミッションをクリア
                # user.user_permissions.clear()
                # プリセットのパーミッションをユーザーに追加
                for perm in preset.permissions.all():
                    user.user_permissions.add(perm.permission)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"ユーザー '{user.username}' にパーミッションを設定しました。"))