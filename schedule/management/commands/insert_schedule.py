from django.core.management.base import BaseCommand
from schedule.models import Schedule
from user.models import Tenant
from music.models import Music

from uuid import uuid4
from datetime import date, timedelta, time
import random

# コマンドの実行方法: python manage.py insert_schedule
class Command(BaseCommand):
    help = '3か月分の土日スケジュールをTenantごとに作成します（タイトル・場所・練習メニュー付き）'
    def handle(self, *args, **kwargs):
        Schedule.objects.all().delete()
        tenants = Tenant.objects.all()
        musics = Music.objects.all()

        if not tenants.exists() or not musics.exists():
            self.stdout.write(self.style.ERROR("TenantまたはMusicが存在しません"))
            return

        today = date.today()
        end_date = today + timedelta(days=90)

        # 土日だけ抽出
        all_dates = [today + timedelta(days=i) for i in range((end_date - today).days + 1)]
        weekend_dates = [d for d in all_dates if d.weekday() in [5, 6]]  # 5=土曜, 6=日曜

        titles = ["合奏", "個人練習", "本番"]
        places = ["市民ホール", "音楽室A", "音楽室B", "文化会館", "練習スタジオ"]

        for tenant in tenants:
            tenant_musics = musics.filter(tenant=tenant)
            if not tenant_musics.exists():
                self.stdout.write(self.style.WARNING(f"{tenant.name} に対応するMusicがありません"))
                continue

            for d in weekend_dates:
                # 1～6件のScheduleをランダム生成
                num_schedules = random.randint(1, 6)
                for _ in range(num_schedules):
                    title = random.choice(titles)
                    place = random.choice(places)
                    # 練習メニュー（改行あり）
                    if title == "合奏":
                        note = "13:00〜14:30 ウォームアップ\n14:30〜16:00 合奏練習\n16:00〜17:00 セクション練習"
                    elif title == "個人練習":
                        note = "13:00〜15:00 個人練習\n15:00〜17:00 パートごとの確認"
                    else:  # 本番
                        note = "13:00 集合・準備\n14:00 開演\n16:00 終演・片付け"

                    schedule = Schedule.objects.create(
                        id=uuid4(),
                        date=d,
                        start=time(hour=13, minute=0),
                        end=time(hour=17, minute=0),
                        title=title,
                        place=place,
                        note=note,
                        tenant=tenant
                    )

                    selected_musics = random.sample(list(tenant_musics), k=min(len(tenant_musics), random.randint(2, 4)))
                    schedule.music.set(selected_musics)

                    self.stdout.write(self.style.SUCCESS(
                        f"{tenant.name} のスケジュール作成: {d} [{title}] 曲数: {len(selected_musics)}"
                    ))

                selected_musics = random.sample(list(tenant_musics), k=min(len(tenant_musics), random.randint(2, 4)))
                schedule.music.set(selected_musics)

                self.stdout.write(self.style.SUCCESS(
                    f"{tenant.name} のスケジュール作成: {d} [{title}] 曲数: {len(selected_musics)}"
                ))


                # 最大文字数のスケジュールを作成
                long_title = "非常に長いタイトルのスケジュール" + "あ" * (255 - len("非常に長いタイトルのスケジュール"))  # 255文字のタイトル
                long_place = "非常に長い場所の名前" + "あ" * (255 - len("非常に長い場所の名前"))  # 255文字の場所
                long_note = "非常に長い活動内容の説明" + "あ" * (20000 - len("非常に長い活動内容の説明"))  # 20000文字の活動内容
                all_musics = tenant_musics
                Schedule.objects.create(
                    id=uuid4(),
                    date=d,
                    start=time(hour=13, minute=0),
                    end=time(hour=17, minute=0),
                    title=long_title,
                    place=long_place,
                    note=long_note,
                    tenant=tenant
                ).music.set(all_musics)  # 全曲を紐づけたスケジュールを作成

                self.stdout.write(self.style.SUCCESS(
                    "非常に長いタイトルのスケジュール作成"
                ))
