from django.core.management.base import BaseCommand
from music.models import Music, Formation
from instrument.models import Instrument
from user.models import Tenant, TenantUser
from datetime import date, timedelta
import random


titles = [
            "アルメニアン・ダンス パート1", "アルメニアン・ダンス パート2", "吹奏楽のための第一組曲", "吹奏楽のための第二組曲",
            "エル・カミーノ・レアル", "フェスティヴァル・ヴァリエーションズ", "ジュビリー序曲", "マーチ「ブルースカイ」",
            "マーチ「プロヴァンスの風」", "マーチ「春風の通り道」", "マーチ「エイプリル・リーフ」", "マーチ「夢の翼」",
            "マーチ「ベスト・フレンド」", "マーチ「希望の光」", "マーチ「未来への展開」", "マーチ「虹色の風」",
            "マーチ「煌めきの朝」", "マーチ「陽光の街」", "マーチ「風の通り道」", "マーチ「青空と太陽」",
            "マーチ「光と風の通り道」", "マーチ「春の喜び」", "マーチ「明日への扉」", "マーチ「輝く未来」",
            "マーチ「希望の空」", "マーチ「風の旅人」", "マーチ「陽だまりの道」", "マーチ「空に舞う」",
            "マーチ「風のメロディ」", "マーチ「光の彼方へ」", "マーチ「未来へのフライト」", "マーチ「空と風の詩」",
            "マーチ「風のシンフォニー」", "マーチ「光のファンファーレ」", "マーチ「希望のファンファーレ」",
            "マーチ「空のファンタジー」", "マーチ「風のファンタジー」", "マーチ「光のファンタジー」",
            "マーチ「未来のファンタジー」", "マーチ「空の冒険」", "マーチ「風の冒険」", "マーチ「光の冒険」",
            "マーチ「未来の冒険」", "マーチ「空の物語」", "マーチ「風の物語」", "マーチ「光の物語」",
            "マーチ「未来の物語」", "マーチ「空の記憶」", "マーチ「風の記憶」", "マーチ「光の記憶」"
        ]
composers = ["A. Reed", "P. Sparke", "J. Barnes", "J. de Meij", "真島俊夫", "福田洋介", "建部知弘", "高昌帥", "和田直也", "中橋愛生"]
arrangers = ["星出尚志", "森田一浩", "鈴木英史", "小編成版編曲者", "オリジナル", "編曲なし", "山口哲人", "樽屋雅徳", "清水大輔", "八木澤教司"]
sections = ["1st", "2nd", "3rd"]

# コマンドの実行方法: python manage.py insert_music
class Command(BaseCommand):
    help = '吹奏楽曲のサンプルデータを50件作成します'

    def handle(self, *args, **kwargs):
        Music.objects.all().delete()
        
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.ERROR("Tenantが存在しません。先にTenantを作成してください。"))
            return

        for tenant in tenants:
            instruments = Instrument.objects.filter(tenant=tenant)
            if not instruments.exists():
                self.stdout.write(self.style.ERROR(f"Tenant {tenant.name} に楽器が存在しません。先に楽器を作成してください。"))
                continue

            for t in titles:
                music = Music.objects.create(
                    title=t,
                    composer=random.choice(composers),
                    arranger=random.choice(arrangers),
                    tenant=tenant,
                    note=f"これは{t}のサンプルデータです。",
                    is_show=True
                )
                
                users_qs = TenantUser.objects.filter(tenant=tenant)
                if not users_qs.exists():
                    self.stdout.write(self.style.ERROR(f"Tenant {tenant.name} にユーザーが存在しません。先にユーザーを作成してください。"))
                    continue

                users = list(users_qs)
            
                for instrument in instruments:
                    for section in sections:
                        formation = Formation.objects.create(
                            music=music,
                            section=section,
                            instrument=instrument,
                            tenant=tenant
                        )
                        # 楽団に属するユーザーをランダムに1〜3人追加
                        group_size = min(len(users), random.randint(1, 3))
                        selected = [users.pop() for _ in range(group_size)]
                        formation.users.set(selected)
                        formation.save()

                    
                        if len(users) == 0:
                            break  # ユーザーが足りなくなったら終了
                    if len(users) == 0:
                            break  # ユーザーが足りなくなったら終了
                self.stdout.write(self.style.SUCCESS(f"Inserted music: {music.title} for tenant {tenant.name}"))
            

            # 最大文字数の曲も追加
            long_title = ["L" * 255, "長" * 255]  # 255文字のタイトルと、50回繰り返したタイトルの両方を用意
            long_composer = ["C" * 255, "作" * 255]
            long_arranger = ["A" * 255, "編" * 255]
            long_note = ["N" * 20000, "備" * 20000]
            for i in range(2):  # それぞれのパターンで1件ずつ作成
                music = Music.objects.create(
                    title=long_title[i],
                    composer=long_composer[i],
                    arranger=long_arranger[i],
                    tenant=tenant,
                    note=long_note[i],
                    is_show=True
                )

                users_qs = TenantUser.objects.filter(tenant=tenant)
                long_section = ["S" * 50 , "せ" * 50 , "セ" * 50]
                for instrument in instruments:
                    formation = Formation.objects.create(
                        music=music,
                        section=random.choice(long_section),
                        instrument=instrument,
                        tenant=tenant
                    )
                    # 楽団に属するユーザーを全員追加
                    users = list(users_qs)
                    formation.users.set(users)
                    formation.save()
                self.stdout.write(self.style.SUCCESS(f"Inserted music: {music.title} for tenant {tenant.name}"))


        self.stdout.write(self.style.SUCCESS("Music insertion completed."))