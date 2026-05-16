from django.core.management.base import BaseCommand
from schedule.models import Schedule, Attendance
from user.models import Tenant, TenantUser
from music.models import Music

from uuid import uuid4
from datetime import date, timedelta, time
import random

# コマンドの実行方法: python manage.py insert_attendance
class Command(BaseCommand):
    help = 'スケジュールに対して出欠情報をランダムに追加します'
    def handle(self, *args, **kwargs):
        tenants = Tenant.objects.all()
        
        if not tenants.exists():
            self.stdout.write(self.style.ERROR("Tenantが存在しません"))
            return

        ATTENDANCE_CHOICES_COPY = Attendance.ATTENDANCE_CHOICES

        # 出欠情報を全削除
        Attendance.objects.all().delete()

        for tenant in tenants:
            schedules = Schedule.objects.filter(tenant=tenant)
            users = TenantUser.objects.filter(tenant=tenant)

            if not schedules.exists():
                self.stdout.write(self.style.WARNING(f"Tenant {tenant.name} にスケジュールが存在しません"))
                continue
            if not users.exists():
                self.stdout.write(self.style.WARNING(f"Tenant {tenant.name} にユーザーが存在しません"))
                continue

            for schedule in schedules:
                for user in users:
                    # ランダムに出欠ステータスを選択
                    status = random.choice(ATTENDANCE_CHOICES_COPY)

                    note = ""
                    # 遅刻ならnoteに理由を追加
                    if status[0] == 2:
                        note = f"遅刻理由: {random.choice(['交通渋滞', '寝坊', '体調不良'])}"
                    elif status[0] == 3:
                        note = f"早退理由: {random.choice(['仕事の都合', '家族の用事', '体調次第'])}"
                    elif status[0] == 4:
                        note = f"欠席理由: {random.choice(['仕事の都合', '家族の用事', '体調次第'])}"
                    elif status[0] == 5:
                        note = f"未定理由: {random.choice(['仕事の都合', '家族の用事', '体調次第'])}"

                    # 出欠情報をスケジュールに追加
                    Attendance.objects.create(
                        schedule=schedule,
                        user=user,
                        status=status[0],
                        note=note,
                        tenant=tenant
                    )

        self.stdout.write(self.style.SUCCESS("出欠情報の挿入が完了しました"))