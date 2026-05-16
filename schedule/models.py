from django.db import models
import uuid
import datetime
from user.models import Tenant, TenantUser
from music.models import Music
from urllib.parse import urlparse


def datetime_formatter(date):
    if datetime.datetime.now().year == date.year:
        return date.strftime('%m月%d日%H:%M~')
    return date.strftime('%Y年%m月%d日%H:%M~')


def date_formatter(date):
    if datetime.datetime.now().year == date.year:
        return date.strftime('%m月%d日')
    return date.strftime('%Y年%m月%d日')


def schedule_title_formatter(place):
    return f' @{place} ' if place else ' @場所未定 '


# Create your models here.
class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(blank=False, verbose_name="日付")
    start = models.TimeField(blank=False, verbose_name="開始時刻")
    end = models.TimeField(blank=False, verbose_name="終了時刻")
    title = models.CharField(blank=False, max_length=255, verbose_name="活動名")
    place = models.CharField(verbose_name='場所', null=True, blank=True, max_length=255)
    place_map_url = models.URLField(verbose_name='場所の地図URL', null=True, blank=True)
    note = models.TextField(blank=True, max_length=20000, verbose_name='活動内容')
    music = models.ManyToManyField(Music, null=True, blank=True, verbose_name='演奏曲')

    tenant = models.ForeignKey(Tenant, null=False, blank=False, verbose_name="楽団", on_delete=models.CASCADE)

    class Meta:
        db_table = 'tenant_schedule'
        verbose_name = "活動予定"
        verbose_name_plural = "活動予定"

    def __str__(self):
        return self.create_schedule_str()

    def create_schedule_str(self, br=False):
        date = datetime_formatter(self.date)
        place = schedule_title_formatter(self.place)
        title = self.title
        if br:
            return "{}<br>{}<br>{}".format(date, place, title)
        else:
            return date + place + title

    def get_attendance(self):
        participants = Attendance.objects.filter(schedule=self.id)
        attend_count = [0, 0, 0, 0]  # 0:未回答 1:出席 2:欠席 3:未定
        for a in participants:
            attend_count[a.status] += 1
        return '{}'.format(attend_count[1] + attend_count[3])

    def get_tags(self):
        ret = []
        for tag in self.tags.all():
            ret.append(tag.__str__())

        return ret

    def get_id(self):
        return str(self.id)

    def valid_place_map_url(self):
        if not self.place_map_url:
            return False
        try:
            p = urlparse(self.place_map_url)
        except Exception:
            return False
        if p.scheme not in ('http', 'https'):
            return False
        host = p.netloc.lower()
        allowed_domains = ('google.com', 'google.co.jp', 'goo.gl', 'maps.app.goo.gl')
        if any(host == d or host.endswith('.' + d) for d in allowed_domains):
            return True
        return False


class Attendance(models.Model):
    ATTENDANCE_CHOICES = (
        (0, '未回答'),
        (1, '出席'),
        (2, '遅刻'),
        (3, '早退'),
        (4, '欠席'),
        (5, '未定'),
        (6, '休団中')  # 出欠回答の選択肢には表示しない
    )

    # 自由が入力欄が必要かどうかの設定
    REQUIRED_NOTE = (
        (0, False),  # 未回答
        (1, False),  # 出席
        (2, True),  # 遅刻
        (3, True),  #早退
        (4, True),  # 欠席
        (5, True),  # 未定
        (6, False)   # 休団中
    )

    NOTE_MAX_LENGTH = 255
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(Schedule, verbose_name='活動', on_delete=models.CASCADE, related_name="schedule")
    user = models.ForeignKey(TenantUser, verbose_name='回答者', on_delete=models.CASCADE, related_name="user")
    status = models.IntegerField(verbose_name='出欠', choices=ATTENDANCE_CHOICES, default=0)
    note = models.CharField(max_length=NOTE_MAX_LENGTH, verbose_name='事由', blank=True)
    check_in = models.BooleanField(verbose_name='チェックイン', default=False)  # チェックインの有無を記録するフィールド

    tenant = models.ForeignKey(Tenant, null=False, blank=False, verbose_name="楽団", on_delete=models.CASCADE)

    class Meta:
        db_table = 'tenant_attendance'
        verbose_name = "出欠"
        verbose_name_plural = "出欠"

        constraints = [
            # abc_idとxyz_cdでユニーク制約
            models.UniqueConstraint(fields=['schedule', 'user'], name='unique_attendance')
        ]

    def __str__(self):
        return self.user.__str__()


class ScheduleLog(models.Model):
    # AttendanceモデルのATTENDANCE_CHOICESと対応させること
    ATTENDANCE_STATUS_CHOICES = (
        (1, '出席'),
        (4, '欠席'),
        (6, '休団')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule_id = models.UUIDField(verbose_name='スケジュールID')
    date = models.DateField(blank=False, verbose_name="日付")
    start = models.TimeField(blank=False, verbose_name="開始時刻")
    end = models.TimeField(blank=False, verbose_name="終了時刻")
    title = models.CharField(blank=False, max_length=255, verbose_name="活動名")
    place = models.CharField(verbose_name='場所', null=True, blank=True)
    note = models.TextField(blank=True, verbose_name='活動内容')
    music = models.TextField(null=True, blank=True, verbose_name='演奏曲')
    attendance = models.JSONField(null=True, blank=True, verbose_name='出欠情報')  # 出欠情報をJSON形式で保存するフィールド

    tenant = models.ForeignKey(Tenant, null=False, blank=False, verbose_name="楽団", on_delete=models.CASCADE)

    class Meta:
        db_table = 'tenant_schedule_log'
        verbose_name = "活動履歴"
        verbose_name_plural = "活動履歴"

    def __str__(self):
        return f"{self.title} - {self.date} - {self.start} - {self.end}"
    