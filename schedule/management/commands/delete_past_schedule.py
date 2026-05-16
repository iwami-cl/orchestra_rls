from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from schedule.models import Schedule

# 保存期間を過ぎたスケジュールを削除するコマンド 実行方法: python manage.py delete_past_schedule
class Command(BaseCommand):
    help = '保存期間を過ぎたスケジュールを削除します'

    def handle(self, *args, **kwargs):
        today = date.today()

        # 正確に「◯年前の同じ日」を求める
        cutoff_date = today - relativedelta(years=settings.SCHEDULE_RETENTION_DAYS)

        past_schedules = Schedule.objects.filter(date__lt=cutoff_date)
        count = past_schedules.count()
        past_schedules.delete()

        self.stdout.write(self.style.SUCCESS(f'{count}件の過去のスケジュールを削除しました。'))
