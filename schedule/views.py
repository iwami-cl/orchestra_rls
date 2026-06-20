import json
from multiprocessing import context
from time import timezone
import datetime
from django.forms import ValidationError
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import resolve_url
from django.urls import reverse_lazy, reverse
from django.views import generic as generic_view

from common.views import OrchestraDeleteMixin, OrchestraPermissionRequiredMixin
from music.models import Formation
from schedule.api.serializer import AttendanceCheckForUserSerializer, AttendanceForScheduleSerializer
from .models import Schedule, Attendance, ScheduleLog
from .forms import ScheduleForm
from user.models import LeaveApplication, TenantUser, Tenant

from django.shortcuts import redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Exists, OuterRef, Subquery


# Create your views here.
class ScheduleCreateView(OrchestraPermissionRequiredMixin, generic_view.CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "schedule/schedule_create.html"
    success_url = reverse_lazy('schedule:schedule_list')

    permission_required = "schedule.add_schedule"
    permission_redirect_url = reverse_lazy('schedule:schedule_list')
    permission_denied_message = "スケジュールの作成権限がありません。"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ログインユーザーを渡す

        date_param = self.request.GET.get('date', None)
        if date_param:
            try:
                kwargs['date'] = date_param
            except (ValueError, TypeError):
                kwargs['date'] = None

        return kwargs

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        ret = super().form_valid(form)
        if ret:
            users = TenantUser.objects.all()
            for u in users:
                attendance = Attendance.objects.create(
                    schedule=self.object,
                    user=u,
                    tenant=u.tenant
                )
                attendance.save()
            return ret
        else:
            return ret
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = False
        context['cancel_url'] = reverse("schedule:schedule_list")
        context['model'] = self.model._meta.verbose_name
        return context


class ScheduleUpdateView(OrchestraPermissionRequiredMixin, generic_view.UpdateView):
    permission_required = "schedule.change_schedule"
    permission_denied_message = "スケジュールの編集権限がありません。"

    model = Schedule
    form_class = ScheduleForm
    template_name = "schedule/schedule_create.html"

    def permission_redirect_url(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return reverse("schedule:schedule_detail", kwargs={"pk": pk})
    
    def get_success_url(self):
        return reverse("schedule:schedule_detail", kwargs={"pk": self.object.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ログインユーザーを渡す
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        context['cancel_url'] = reverse("schedule:schedule_detail", kwargs={"pk": self.object.pk})
        context['model'] = self.model._meta.verbose_name
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))


class ScheduleDetailView(OrchestraPermissionRequiredMixin, generic_view.DetailView):
    model = Schedule
    template_name = "schedule/schedule_detail.html"
    permission_required = "schedule.view_schedule"
    permission_redirect_url = reverse_lazy('schedule:schedule_list')
    permission_denied_message = "スケジュールの閲覧権限がありません。"


# スケジュールの一覧表示
class ScheduleListView(OrchestraPermissionRequiredMixin, generic_view.TemplateView):
    template_name = "schedule/schedule_list.html"

    permission_required = "schedule.view_schedule"
    permission_redirect_url = reverse_lazy('index')
    permission_denied_message = "スケジュールの閲覧権限がありません。"

    # 回答が必要なスケジュール数をカウントしてテンプレートに渡す
    def count_unanswered_schedules(self):
        today = datetime.date.today()
        events_count = Schedule.objects.filter(
            date__gte=today
        ).count()

        # 出席/遅刻/早退/欠席のスケジュール数をカウント
        attendance_count = Attendance.objects.filter(
            schedule__date__gte=today,
            user=self.request.user,
            status__in=[1, 2, 3, 4]
        ).count()

        return events_count - attendance_count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Attendance.ATTENDANCE_CHOICESとAttendance.REQUIRED_NOTE_CHOICESを結合して辞書を作成
        # 休団中の選択肢を出欠選択肢から除外
        attencane_choices = [choice for choice in Attendance.ATTENDANCE_CHOICES if choice[0] != 6]
        require_note = [note for note in Attendance.REQUIRED_NOTE if note[0] != 6]
        context["select_attendance"] = [(k[0], k[1], v[1]) for k, v in zip(attencane_choices, require_note)]  # 出欠選択肢と自由入力欄の設定を結合
        last_attendance = Attendance.objects.filter(user=self.request.user,
                                                    schedule__date__gte=datetime.datetime.now().date()).all().order_by(
            "schedule__date").first()
        if last_attendance is not None:
            context.update({"last_schedule": last_attendance.schedule, "last_attendance": last_attendance})
        
        # 回答が必要なスケジュール数をカウントしてテンプレートに渡す
        context['unanswered_count'] = self.count_unanswered_schedules()

        # スケジュールに対する権限をテンプレートに渡す
        context['can_create'] = self.request.user.has_perm('schedule.add_schedule') or self.request.user.role == "admin"
        return context


class ScheduleDeleteView(OrchestraPermissionRequiredMixin, OrchestraDeleteMixin, generic_view.DeleteView):
    model = Schedule
    template_name = "schedule/schedule_delete.html"
    success_url = reverse_lazy('schedule:schedule_list')

    permission_required = "schedule.delete_schedule"
    permission_redirect_url = reverse_lazy('schedule:schedule_list')
    permission_denied_message = "スケジュールの削除権限がありません。"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('schedule:schedule_detail', kwargs={'pk': self.object.pk})
        return context


"""
出欠確認機能のビュー
"""
class AttendanceCheckView(OrchestraPermissionRequiredMixin, generic_view.TemplateView):
    permission_required = "schedule.change_attendance"
    permission_denied_message = "出欠の変更権限がありません。"
    template_name = "schedule/attendance_check.html"
    STATUS_CHOICE_PREFIX = "status_"
    NOTE_PREFIX = "note_"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        schedule = Schedule.objects.filter(id=pk).first()
        if not schedule:
            messages.error(request, "スケジュールが見つかりませんでした。")
            return redirect('schedule:schedule_list')
        
        # 団員一覧に出欠テーブルを左外結合して、ユーザーごとの出欠情報を取得する
        attendance = Attendance.objects.filter(schedule=pk, user=OuterRef("pk"))
        leave_qs = LeaveApplication.objects.filter(user=OuterRef("pk"))

        users = TenantUser.objects.annotate(
            has_leave=Exists(leave_qs),
            attendance_status=Subquery(attendance.values("status")[:1]),
            attendance_note=Subquery(attendance.values("note")[:1]),
        ).order_by('instrument__order', 'instrument__jp_name', 'username')
        context = self.get_context_data()
        
        context.update({
            "schedule": schedule,
            "users": users,
            "attendance_max_length": Attendance._meta.get_field("note").max_length,
        })
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        schedule_id = kwargs.get("pk")
        schedule = Schedule.objects.filter(id=schedule_id).first()
        if not schedule:
            messages.error(request, "スケジュールが見つかりませんでした。")
            return redirect('schedule:schedule_list')
        
        users = TenantUser.objects.all()
        attendance_data = []
        for user in users:
            status_key = f"{self.STATUS_CHOICE_PREFIX}{user.user_id}"
            note_key = f"{self.NOTE_PREFIX}{user.user_id}"
            status = request.POST.get(status_key, None)
            note = request.POST.get(note_key, "")
            if status is not None:
                # AttendanceCheckForUserSerializerでバリデーションを行う
                serializer = AttendanceCheckForUserSerializer(data={
                    "user_id": str(user.user_id),
                    "username": user.username,
                    "display_name": user.get_display_name(),
                    "status": int(status),
                    "note": note
                })
                if serializer.is_valid():
                    user_attendance = serializer.data
                else:
                    messages.error(request, f"ユーザーID: {user.user_id} の出欠データが不正です。")

                    # サーバーログにバリデーションエラーの詳細を出力する
                    print(f"Validation error for user_id {user.user_id}: {serializer.errors}")
                    return redirect('schedule:schedule_detail', pk=schedule_id)
                
                attendance_data.append(user_attendance)
        
        try:
            with transaction.atomic():
                # 「,」区切りで曲名を連結して保存する（曲名の「,」はエンコードする）
                music_titles = ""
                for music in schedule.music.all():
                    title = music.title.replace(",", "%2C")  # 曲名に「,」が含まれている場合はエンコードする
                    if music_titles:
                        music_titles += ","
                    music_titles += title
                fields = {
                    "date": schedule.date,
                    "start": schedule.start,
                    "end": schedule.end,
                    "title": schedule.title,
                    "place": schedule.place,
                    "note": schedule.note,
                    "music": music_titles,
                    "attendance": json.dumps(attendance_data),
                }

                schedule_log, created = ScheduleLog.objects.get_or_create(
                    schedule_id=schedule.id,
                    tenant=schedule.tenant,
                    defaults=fields,
                )

                if not created:
                    for key, value in fields.items():
                        setattr(schedule_log, key, value)
                    schedule_log.save()
                    messages.success(request, "出欠情報を更新しました。")
                else:
                    messages.success(request, "出欠情報を保存しました。")
        
        except ValidationError as ve:
            messages.error(request, f"出欠データの保存に失敗しました: {ve.message}")
        except Exception as e:
            messages.error(request, f"予期せぬエラーが発生しました")
            print(f"Error saving ScheduleLog: {str(e)}")
        
        return redirect('schedule:schedule_detail', pk=schedule_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse("schedule:schedule_detail", kwargs={"pk": self.kwargs.get("pk")})
        return context


# 活動履歴の一覧を表示するビュー
class ScheduleLogListView(OrchestraPermissionRequiredMixin, generic_view.ListView):
    model = ScheduleLog
    template_name = "schedule/schedule_log_list.html"
    context_object_name = "schedule_logs"
    paginate_by = 20

    permission_required = "schedule.view_schedulelog"
    permission_redirect_url = reverse_lazy('index')
    permission_denied_message = "活動履歴の閲覧権限がありません。"


# 活動履歴の詳細を表示するビュー
class ScheduleLogDetailView(OrchestraPermissionRequiredMixin, generic_view.DetailView):
    model = ScheduleLog
    template_name = "schedule/schedule_log_detail.html"
    context_object_name = "schedule_log"

    permission_required = "schedule.view_schedulelog"
    permission_redirect_url = reverse_lazy('index')
    permission_denied_message = "活動履歴の閲覧権限がありません。"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse("schedule:schedule_log_list")
        attendance_list = self.object.attendance
        if attendance_list:
            try:
                # 出欠のjsonを辞書に変換してテンプレートに渡す（この時、HTMLタグをエスケープして渡す）
                load_attendance = json.loads(attendance_list)
                for a in load_attendance:
                    a["username"] = a["username"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    a["note"] = a["note"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                context['attendance_list'] = load_attendance
                context['tabulated_attendance'] = self.tabulation_attendance(load_attendance)
            except json.JSONDecodeError:
                context['attendance_list'] = []
        return context
    
    def tabulation_attendance(self, attendance_list):
        # 出席人数・欠席人数・出席率を集計して、テンプレートに渡すための辞書を作成する
        tabulated_attendance = {
            1: 0,  # 出席
            4: 0,  # 欠席
            6: 0,  # 休団
            "rate": 0.0,  # 出席率
        }
        for attendance in attendance_list:
            try:
                status = int(attendance.get("status"))
                if status in tabulated_attendance:
                    tabulated_attendance[status] += 1
            except (ValueError, TypeError):
                continue
        total = tabulated_attendance[1] + tabulated_attendance[4] + tabulated_attendance[6]
        if total > 0:
            # 出席率を計算。少数第2位を切り捨てて表示する
            rate = tabulated_attendance[1] / total * 100
            tabulated_attendance["rate"] = int(rate * 10) / 10
        return tabulated_attendance



class ScheduleLogDeleteView(OrchestraPermissionRequiredMixin, OrchestraDeleteMixin, generic_view.DeleteView):
    model = ScheduleLog
    template_name = "schedule/schedule_log_delete.html"
    success_url = reverse_lazy('schedule:schedule_log_list')

    permission_required = "schedule.delete_schedulelog"
    permission_redirect_url = reverse_lazy('schedule:schedule_log_list')
    permission_denied_message = "活動履歴の削除権限がありません。"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('schedule:schedule_log_detail', kwargs={'pk': self.object.pk})
        return context