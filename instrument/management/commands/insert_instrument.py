from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from user.models import Tenant, TenantUser
from instrument.models import Instrument  # モデルをインポート
from django.db.utils import IntegrityError


instruments_preset = [
    {"name": "Flute", "initial": "Fl", "jp-name": "フルート"},
    {"name": "Piccolo", "initial": "Pc", "jp-name": "ピッコロ"},
    {"name": "B♭ Clarinet", "initial": "BbCl", "jp-name": "B♭クラリネット"},
    {"name": "E♭ Clarinet", "initial": "EbCl", "jp-name": "E♭クラリネット"},
    {"name": "Bass Clarinet", "initial": "BCl", "jp-name": "バスクラリネット"},
    {"name": "Alto Clarinet", "initial": "ACl", "jp-name": "アルトクラリネット"},
    {"name": "Bassoon", "initial": "Bn", "jp-name": "バスーン"},
    {"name": "Alto Saxophone", "initial": "ASx", "jp-name": "アルトサクソフォン"},
    {"name": "Tenor Saxophone", "initial": "TSx", "jp-name": "テナーサクソフォン"},
    {"name": "Baritone Saxophone", "initial": "BSx", "jp-name": "バリトンサクソフォン"},
    {"name": "Oboe", "initial": "Ob", "jp-name": "オーボエ"},
    {"name": "English Horn", "initial": "EH", "jp-name": "イングリッシュホルン"},
    {"name": "Trumpet", "initial": "Tp", "jp-name": "トランペット"},
    {"name": "Trombone", "initial": "Tb", "jp-name": "トロンボーン"},
    {"name": "Horn", "initial": "Hr", "jp-name": "ホルン"},
    {"name": "Euphonium", "initial": "Eu", "jp-name": "ユーフォニアム"},
    {"name": "Tuba", "initial": "Tu", "jp-name": "チューバ"},
    {"name": "Percussion", "initial": "Pd", "jp-name": "打楽器"},
    {"name": "P"*255, "initial": "P"*255, "jp-name": "ピ"*255},
]

# コマンドの実行方法: python manage.py insert_instrument
class Command(BaseCommand):
    help = '楽器のサンプルデータを各テナントに挿入します'

    def handle(self, *args, **kwargs):
        try:
            tenants = Tenant.objects.all()
            if not tenants.exists():
                print("No tenants found, skipping instrument insertion.")
                print("Please execute python manage.py insert_tenant.")
                return
            
            for tenant in tenants:
                for item in instruments_preset:
                    obj, created = Instrument.objects.get_or_create(
                        name=item["name"],
                        tenant=tenant,
                        defaults={
                            "initial": item["initial"],
                            "jp_name": item["jp-name"]
                        }
                    )
                    if not created:
                        # 登録済みの場合は情報を更新
                        print(f"Instrument {item['name']} already exists for tenant {tenant.name}, updating info.")
                        obj.initial = item["initial"]
                        obj.jp_name = item["jp-name"]
                        obj.save()
                    else:
                        print(f"Inserted instrument {item['name']} for tenant {tenant.name}.")
            print("Instruments insertion completed.")
        except IntegrityError as e:
            pass