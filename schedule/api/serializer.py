from rest_framework.serializers import (
    ModelSerializer,
    IntegerField, SerializerMethodField, DateField, TimeField, CharField, UUIDField
)
from instrument.models import Instrument, InstrumentPart
from music.models import Formation, Music
import schedule
from schedule.models import Schedule, Attendance, ScheduleLog
from rest_framework import serializers
from schedule.models import Schedule
from django.db.models import ObjectDoesNotExist
from user.models import LeaveApplication, TenantUser


class ScheduleSerializer(ModelSerializer):
    place = SerializerMethodField()
    note = SerializerMethodField()
    date = DateField(format="%Y-%m-%d")
    start = TimeField(format="%H:%M")
    end = TimeField(format="%H:%M")
    my_attendance = SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ("id", "title", "place", "date", "start", "end", "note", "my_attendance")

    def get_place(self, instance):
        if instance.place is not None and instance.place:
            return instance.place
        else:
            return "未定"

    def get_note(self, instance):
        if instance.note is not None and instance.note:
            return instance.note
        else:
            return "未定"
        
    def get_my_attendance(self, instance):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            try:
                attendance = Attendance.objects.get(schedule=instance, user=request.user)
                return {
                    "status": attendance.status,
                    "note": attendance.note
                }
            except Attendance.DoesNotExist:
                return {
                    "status": 0,  # 未回答
                    "note": ""
                }
        return {
            "status": 0,
            "note": ""
        }


class AttendanceCreateUpdateSerializer(ModelSerializer):
    status = IntegerField(required=True)
    schedule_id = UUIDField(write_only=True, required=True)
    note = CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Attendance
        fields = ("schedule_id", "status", "note")

    def validate_schedule_id(self, value):
        try:
            return Schedule.objects.get(pk=value)
        except Schedule.DoesNotExist:
            raise serializers.ValidationError("Schedule not found")

    def create(self, validated_data):
        schedule = validated_data.pop("schedule_id")
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("Request user is required")
        user = request.user

        attendance, _ = Attendance.objects.update_or_create(
            schedule=schedule,
            user=user,
            tenant=user.tenant,
            defaults={"status": validated_data.get("status", 0), "note": validated_data.get("note", "")},
        )

        return attendance


class AttendanceForScheduleSerializer(serializers.Serializer):
    attendances = serializers.SerializerMethodField()

    def attendance_for_part(self, schedule):
        attendance = Attendance.objects.filter(schedule=schedule)
        attendance_for_part = {}  # キーはinstrument_id

        # 楽器一覧を取得
        parts = Instrument.objects.all().order_by('order', 'jp_name')
        for p in parts:
            part_id = str(p.id)
            if part_id not in attendance_for_part.keys():  # 楽器ごとに初期化
                attendance_for_part[part_id] = {
                    "instrument_name": p.jp_name if p.jp_name else p.name,
                    'attend': [0,0,0,0,0,0],  # 未回答、出席、遅刻、早退、欠席、未定
                    "users": [],
                }

        # 休団中のユーザー一覧を取得
        leave_users = LeaveApplication.objects.filter(start_date__lte=schedule.date, end_date__gte=schedule.date).values_list('user_id', flat=True)
        leave_users = [str(id) for id in leave_users]  # クエリセットをリストに変換してキャッシュする

        for user in TenantUser.objects.all().order_by('username'):
            # 該当ユーザーの出欠情報を取得
            user_attendance = attendance.filter(user=user).first()

            status = user_attendance.status if user_attendance else 0
            note = user_attendance.note if user_attendance else ""

            # 休団中のユーザーは「欠席・未回答・未定」にしている場合、欠席でカウントする。
            # 出席・遅刻・早退はそのままのステータスでカウントする。
            if (str(user.user_id) in leave_users) and (status in [0, 4, 5]):
                status = 4  # 欠席
                note = "休団中"
            instrument_id = str(user.instrument.id)
            attendance_for_part[instrument_id]['attend'][status] += 1
            attendance_for_part[instrument_id]["users"].append({
                "username": user.get_display_name(),
                "status": status,
                "note": note,
                "section": ""
            })
        return attendance_for_part

    def attendance_for_music(self, schedule, music):
        attendance = Attendance.objects.filter(schedule=schedule)
        attendance_for_music = {}  # キーはinstrument_id

        # FormationからInstrumentをグルーピングして取得
        formations = Formation.objects.filter(music=music).select_related('instrument').prefetch_related('users').order_by('instrument__order', 'section')
        for f in formations:
            f_key_str = str(f.instrument.id)
            if f_key_str not in attendance_for_music.keys():  # 楽器ごとに初期化
                attendance_for_music[f_key_str] = {
                    "instrument_name": f.instrument.jp_name if f.instrument.jp_name else f.instrument.name,
                    'attend': [0,0,0,0,0,0],  # 未回答、出席、遅刻、早退、欠席、未定
                    "users": []
                }

            # 休団中のユーザー一覧を取得
            leave_users = LeaveApplication.objects.filter(start_date__lte=schedule.date, end_date__gte=schedule.date).values_list('user_id', flat=True)
            leave_users = [str(id) for id in leave_users]  # クエリセットをリストに変換してキャッシュする
            
            for user in f.users.all().order_by('username'):
                # 該当ユーザーの出欠情報を取得
                user_attendance = attendance.filter(user=user).first()

                status = user_attendance.status if user_attendance else 0
                note = user_attendance.note if user_attendance else ""

                # 休団中のユーザーは「欠席・未回答・未定」にしている場合、欠席でカウントする。
                # 出席・遅刻・早退はそのままのステータスでカウントする。
                if (str(user.user_id) in leave_users) and (status in [0, 4, 5]):
                    status = 4  # 欠席
                    note = "休団中"

                attendance_for_music[f_key_str]['attend'][status] += 1
                attendance_for_music[f_key_str]["users"].append({
                    "username": user.get_display_name(),
                    "status": status,
                    "note": note,
                    "section": f.section
                })
        return attendance_for_music

    def get_attendances(self, obj: dict):
        schedule_id = obj.get("schedule_id", None)
        music_id = obj.get("music_id", None)
        if schedule_id is not None and music_id is not None:
            schedule = Schedule.objects.filter(id=schedule_id).first()
            music = Music.objects.filter(id=music_id).first()
            if schedule is None or music is None:
                raise serializers.ValidationError("Schedule or Music not found")

            response = self.attendance_for_music(schedule, music)
            return response
        elif schedule_id is not None and music_id is None:
            schedule = Schedule.objects.filter(id=schedule_id).first()
            response = self.attendance_for_part(schedule)
            return response


class AttendanceCheckForUserSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    username = serializers.CharField()
    display_name = serializers.CharField(max_length=255)
    status = serializers.IntegerField()
    note = serializers.CharField(max_length=Attendance.NOTE_MAX_LENGTH, allow_blank=True, allow_null=True)

    def validate_status(self, value):
        if value not in dict(ScheduleLog.ATTENDANCE_STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid attendance status")
        return value


class ScheduleLogSerializer(ModelSerializer):
    place = SerializerMethodField()
    note = SerializerMethodField()
    date = DateField(format="%Y-%m-%d")
    start = TimeField(format="%H:%M")
    end = TimeField(format="%H:%M")

    class Meta:
        model = ScheduleLog
        fields = ("id", "title", "place", "date", "start", "end", "note")

    def get_place(self, instance):
        if instance.place is not None and instance.place:
            return instance.place
        else:
            return "未定"

    def get_note(self, instance):
        if instance.note is not None and instance.note:
            return instance.note
        else:
            return "未定"
