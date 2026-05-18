from django.contrib import messages

from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse

from instrument.models import Instrument
from .forms import LeaveApplicationUpdateForm, LoginFrom, TenantForm, UserForm
from schedule.models import Schedule, Attendance
import datetime
from .models import LeaveApplication, PermissionPreset, Tenant, TenantUser, UserActivateTokens, CustomPermission
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import TenantSignUpForm, PasswordResetForm
from django.shortcuts import render
from django import forms
from django.views.generic import TemplateView
from django.core import signing
from .forms import LeaveApplicationForm
from common.views import OrchestraDeleteMixin, OrchestraPermissionRequiredMixin
import django_filters 
from django_filters.views import FilterView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

# def activate_user(request, activate_token):
#     activated_user = UserActivateTokens.objects.activate_user_by_token(
#         activate_token)
#     if hasattr(activated_user, 'is_active'):
#         if activated_user.is_active:
#             message = 'ユーザーのアクティベーションが完了しました'
#         if not activated_user.is_active:
#             message = 'アクティベーションが失敗しています。管理者に問い合わせてください'
#     if not hasattr(activated_user, 'is_active'):
#         message = 'エラーが発生しました'
#     return HttpResponse(message)

# 利用規約ビュー
def terms_of_service(request):
    return render(request, 'tenant/terms_of_use.html')


# ログインビューを作成
class LoginView(BaseLoginView):
    form_class = LoginFrom
    template_name = "user/login.html"


class LogoutView(BaseLogoutView):
    success_url = reverse_lazy("index")


# メニュー画面のビュー
class IndexView(LoginRequiredMixin, TemplateView):
    """ ホームビュー """
    template_name = "index.html"

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
        context["select_attendance"] = [(k[0], k[1], v[1]) for k, v in zip(Attendance.ATTENDANCE_CHOICES, Attendance.REQUIRED_NOTE)]  # 出欠選択肢と自由入力欄の設定を結合
        last_attendance = Attendance.objects.filter(user=self.request.user,
                                                    schedule__date__gte=datetime.datetime.now().date()).all().order_by(
            "schedule__date").first()
        if last_attendance is not None:
            context.update({"last_schedule": last_attendance.schedule, "last_attendance": last_attendance})
        
        # 回答が必要なスケジュール数をカウントしてテンプレートに渡す
        context['unanswered_count'] = self.count_unanswered_schedules()
        return context


class CreateTenantView(TemplateView):
    """ テナント作成用ビュー """
    template_name = "user/tenant_sign_up.html"
    success_url = reverse_lazy("index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TenantSignUpForm()
        context['title'] = "団体登録"
        context['cancel_url'] = reverse('index')
        return context
    
    def post(self, request, *args, **kwargs):
        form = TenantSignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect(self.success_url)
        return self.get(request, *args, **kwargs)


class PasswordResetView(TemplateView):
    """ パスワードリセットビュー """
    template_name = "user/password_reset.html"
    success_url = reverse_lazy("user:password_reset_success")
    form_class = PasswordResetForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(user_id=self.kwargs.get('pk'))
        context['model'] = self.model._meta.verbose_name if hasattr(self, 'model') else 'ユーザー'
        context['cancel_url'] = reverse('index')
        return context
    
    def get(self, request, *args, **kwargs):
        # URLからユーザーIDを取得
        user_id = request.GET.get('user_id', None)
        # ログイン中なら、user_id必須かつ本人以外のアクセスは団員一覧にリダイレクト
        if request.user.is_authenticated:
            if user_id is None or str(request.user.user_id) != user_id:
                return redirect('user:user_list')
        # 未ログインかつ、user_idがある場合は、user_idをないURLにリダイレクト（セキュリティ上、user_idはURLにあってはならないため）
        elif not request.user.is_authenticated and user_id is not None:
            return redirect('user:password_reset')
        
        # 未ログインユーザーのアクセスはパスワードリセットフォームを表示
        form = self.form_class(user_id=user_id)
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        # URLからユーザーIDを取得
        user_id = request.GET.get('user_id', None)

        # ログイン中かつ、本人以外のアクセスは団員一覧にリダイレクト
        if request.user.is_authenticated and (user_id is None or str(request.user.user_id) != user_id):
            return redirect('user:user_list')
        
        try:
            form = self.form_class(request.POST, user_id=user_id)
            if form.is_valid():
                token = form.save()
                reset_url = request.build_absolute_uri(
                    reverse_lazy('user:password_reset_avtivate')
                ) + f'?token={token.activate_token}'
                return redirect(self.success_url)
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
        except forms.ValidationError as e:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            context['form'].add_error(None, e)
            return self.render_to_response(context)


def password_reset_success(request):
    return render(request, 'user/password_reset_success.html')


def password_reset_avtivate(request):
    token = request.GET.get('token', None)
    if token is not None:
        ret = UserActivateTokens.activate_user_by_token(token)
        if ret:
            return render(request, 'user/password_reset_avtivate.html')
    
    return render(request, 'user/password_reset_fail.html')


class TenantUserListFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr='icontains', label='メールアドレス')
    role = django_filters.ChoiceFilter(method='filter_by_role', label='ロール', choices=TenantUser.ROLE_CHOICES)
    instrument = django_filters.CharFilter(method='filter_by_instrument', label='担当楽器', help_text='楽器名、イニシャル、日本語名のいずれかで検索')

    def filter_by_role(self, queryset, name, value):
        if value == 'admin':
            return queryset.filter(role='admin')
        elif value == 'member':
            return queryset.filter(role='member')
        elif value == 'guest':
            return queryset.filter(role='guest')
        return queryset
    
    def filter_by_instrument(self, queryset, name, value):
        # 楽器名でフィルタリングするため、関連するInstrumentモデルのname, initial, jp_name, フィールドを参照
        instrument = Instrument.objects.filter(
            Q(name__icontains=value) |
            Q(initial__icontains=value) |
            Q(jp_name__icontains=value)
        ).values_list('id', flat=True)

        return queryset.filter(instrument__in=instrument)

    class Meta:
        model = TenantUser
        fields = ['email', 'role', 'instrument']


class TenantUserListView(OrchestraPermissionRequiredMixin, FilterView):
    """ 団員一覧ビュー """
    template_name = "user/user_list.html"
    model = TenantUser

    permission_required = "user.view_tenantuser"
    permission_redirect_url_name = "index"
    permission_denied_message = "団員の閲覧権限がありません。"

    list_display_fields = ["instrument"]
    detail_url_field = None

    paginate_by = 10

    filterset_class = TenantUserListFilter

    def get_queryset(self):
        sort_key = self.request.GET.get('sort', '')
        # ソートキーはカンマ区切りで複数指定可能
        if sort_key:
            sort_key = sort_key.split(',')

            # キーにfull_nameか-full_nameが含まれている場合は、first_name, last_nameに分解する
            if 'full_name' in sort_key:
                sort_key.remove('full_name')
                sort_key.extend(['first_name', 'last_name'])
            if '-full_name' in sort_key:
                sort_key.remove('-full_name')
                sort_key.extend(['-first_name', '-last_name'])
            # RLSなのでテナント単位の絞り込みは不要
            queryset = super().get_queryset().order_by(*sort_key)
            return queryset
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # UserFormをコンテキストに追加
        context['form'] = UserForm(instance=None, login_user=self.request.user)
        
        # ユーザーパーミッションをコンテキストに追加
        context['all_permissions'] = CustomPermission.objects.filter(private=False).select_related('permission')
        presets = PermissionPreset.objects.all()
        # json形式でプリセットの権限情報を作成してコンテキストに追加
        context['permission_presets'] = {
            preset.id: {
                'name': preset.name,
                'permissions': list(preset.permissions.values_list('permission_id', flat=True))
            } for preset in presets
        }

        context['total_count'] = self.get_queryset().count()
        context['model'] = self.model._meta.verbose_name
        context['list_display_fields'] = self.list_display_fields
        context['detail_url_field'] = self.detail_url_field

        return context


class TenantUpdateView(OrchestraPermissionRequiredMixin, UpdateView):
    """ 団体情報変更ビュー """
    model = Tenant
    form_class = TenantForm
    template_name = "tenant/tenant_update.html"
    success_url = reverse_lazy("index")

    permission_required = "tenant.change_tenant"
    permission_denied_message = "団体情報の編集権限がありません。"
    permission_redirect_url_name = "index"

    def get_object(self, queryset=None):
        return self.request.user.tenant
    
    def get_form_class(self):
        return super().get_form_class()


class UserDetailView(TemplateView):
    """ ユーザー詳細ビュー """
    template_name = "user/user_detail.html"

    permission_required = "user.view_tenantuser"
    permission_denied_message = "ユーザーの閲覧権限がありません。"
    permission_redirect_url_name = "user:user_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        context['show_user'] = TenantUser.objects.get(user_id=user_id)

        # UserFormをコンテキストに追加
        context['form'] = UserForm(instance=context['show_user'], login_user=self.request.user)
        
        # ユーザーパーミッションをコンテキストに追加
        context['user_permissions'] = context['show_user'].get_all_permissions()
        context['all_permissions'] = CustomPermission.objects.filter(private=False).select_related('permission')
        presets = PermissionPreset.objects.filter(tenant=context['show_user'].tenant)
        # json形式でプリセットの権限情報を作成してコンテキストに追加
        context['permission_presets'] = {
            preset.id: {
                'name': preset.name,
                'permissions': list(preset.permissions.values_list('permission_id', flat=True))
            } for preset in presets
        }
        return context

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('pk')

        # 本人ならアクセスを許可、それ以外は団員一覧にリダイレクト
        if request.user.user_id == user_id or request.user.has_perm("user.view_tenantuser") or request.user.is_admin():
            return super().get(request, *args, **kwargs)
        else:
            # ユーザー閲覧権限があればアクセスを許可、なければ団員一覧にリダイレクト
            if request.user.has_perm("user.view_tenantuser"):
                return super().get(request, *args, **kwargs)
            return redirect('user:user_list')


# 団員追加ビュー　団員一覧ビューのモーダルからのPOSTリクエストのみを受けるビュー
def tenant_user_update_create_view(request, pk=None):
    if request.method != "POST":
        return HttpResponse(status=405)  # POST以外は許可しない

    # pkがある場合は更新、ない場合は作成とみなす
    if pk:
        if (request.user.user_id != pk and (request.user.has_perm("user.change_tenantuser") or request.user.is_admin())) \
            or request.user.user_id == pk:
            user = TenantUser.objects.get(user_id=pk)
            form = UserForm(request.POST, instance=user, login_user=request.user)
            if form.is_valid():
                user = form.save(commit=False)
                user.tenant = request.user.tenant  # 作成するユーザーのテナントをログインユーザーと同じにする
                user.save()
                user.user_permissions.clear() # これでDjangoのPermissionモデルとの関連もクリアされる
                for perm in form.cleaned_data.get('permissions', []):
                    user.user_permissions.add(perm.permission)  # DjangoのPermissionモデルに関連付け
                return redirect('user:user_detail', pk=pk)
        return redirect('user:user_detail', pk=pk)
    else:
        if not request.user.has_perm("user.add_tenantuser") and not request.user.is_admin():
            messages.error(request, "ユーザーの追加権限がありません。")
            return redirect('user:user_list')
        form = UserForm(request.POST, instance=None, login_user=request.user)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.tenant = request.user.tenant  # 作成するユーザーのテナントをログインユーザーと同じにする
            new_user.save()
            new_user.user_permissions.clear() # これでDjangoのPermissionモデルとの関連もクリアされる
            for perm in form.cleaned_data.get('permissions', []):
                new_user.user_permissions.add(perm.permission)  # DjangoのPermissionモデルに関連付け
            return redirect('user:user_list')
        return redirect('user:user_list')


class TenantUserDeleteView(OrchestraPermissionRequiredMixin, OrchestraDeleteMixin, DeleteView):
    """ 団員削除ビュー """
    model = TenantUser
    template_name = "user/tenant_user_delete.html"
    success_url = reverse_lazy("user:user_list")

    permission_required = "user.delete_tenantuser"
    permission_denied_message = "ユーザーの削除権限がありません。"
    permission_redirect_url_name = "user:user_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('user:user_detail', kwargs={'pk': self.object.user_id})
        return context


class InviteUserForm(forms.Form):
    email = forms.EmailField(label="招待するユーザーのメールアドレス")
    first_name = forms.CharField(label="名", required=False)
    last_name = forms.CharField(label="姓", required=False)


class InviteUserView(LoginRequiredMixin, OrchestraPermissionRequiredMixin, TemplateView):
    """
    団員を招待するビュー。
    - GET: 招待フォームを表示
    - POST: 招待用トークンを生成して招待URLを作成（メール送信は行わずコンソール出力／テンプレートへ返す）
    """
    template_name = "user/invite_user.html"
    form_class = InviteUserForm
    invite_salt = "tenant-invite-salt"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('form', self.form_class())
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        context = self.get_context_data(**kwargs)
        context['form'] = form
        if not form.is_valid():
            return self.render_to_response(context)

        email = form.cleaned_data['email']
        first_name = form.cleaned_data.get('first_name') or ''
        last_name = form.cleaned_data.get('last_name') or ''

        # ペイロードには招待されたメール、招待元テナント/ユーザーを含める
        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tenant_id": getattr(request.user, 'tenant_id', None),
            "inviter_id": getattr(request.user, 'id', None),
        }

        # トークンを生成（必要に応じて expires を受け取って loads 側で検証できます）
        token = signing.dumps(payload, salt=self.invite_salt)

        # 招待を受けるための URL（受け取り側のビュー名を 'user:invite_accept' と仮定）
        accept_path = reverse_lazy('user:invite_accept')
        invite_url = request.build_absolute_uri(f"{accept_path}?token={token}")

        # 実際はここでメール送信を行う（例: send_mail(...)）。とりあえずコンソール出力してテンプレートへ渡す
        print("Invite URL:", invite_url)

        context.update({
            "invite_url": invite_url,
            "sent": True,
            "invited_email": email,
        })
        return self.render_to_response(context)


# 休団申請作成ビュー
class LeaveApplicationCreateView(LoginRequiredMixin, OrchestraPermissionRequiredMixin, CreateView):
    model = LeaveApplication
    form_class = LeaveApplicationForm
    template_name = "user/leave_application_form.html"
    success_url = reverse_lazy("user:leave_application_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today() + datetime.timedelta(days=30),
        }
        return kwargs

    def form_valid(self, form):
        # 期間に重複がないかをチェック
        user = form.cleaned_data['user']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        overlapping_applications = LeaveApplication.objects.filter(
            user=user,
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        if overlapping_applications.exists():
            messages.error(self.request, "同じ期間に重複する休団申請が既に存在しています。")
            return self.form_invalid(form)

        leave_application = form.save(commit=False)
        leave_application.tenant = self.request.user.tenant
        leave_application.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = False
        context['pk'] = self.get_form_kwargs()
        context['model'] = self.model._meta.verbose_name
        context['cancel_url'] = reverse("user:leave_application_list")
        return context


# 休団申請更新ビュー
class LeaveApplicationUpdateView(LoginRequiredMixin, OrchestraPermissionRequiredMixin, UpdateView):
    model = LeaveApplication
    form_class = LeaveApplicationUpdateForm
    template_name = "user/leave_application_form.html"
    success_url = reverse_lazy("user:leave_application_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today() + datetime.timedelta(days=30),
        }
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        context['pk'] = self.get_form_kwargs()
        context['model'] = self.model._meta.verbose_name
        context['cancel_url'] = reverse("user:leave_application_detail", kwargs={'pk': self.object.pk})
        return context

class LeaveApplicationFilter(django_filters.FilterSet):
    user__username = django_filters.CharFilter(lookup_expr='icontains', label='ユーザー名')

    class Meta:
        model = LeaveApplication
        fields = ['user__username']


# 休団申請一覧ビュー
class LeaveApplicationListView(LoginRequiredMixin, OrchestraPermissionRequiredMixin, FilterView):
    model = LeaveApplication
    template_name = "user/leave_application_list.html"
    context_object_name = "leave_applications"
    list_display_fields = ['start_date', 'end_date']
    detail_url_field = "user"
    filterset_class = LeaveApplicationFilter
    permission_required = "user.view_leaveapplication"
    permission_redirect_url_name = "index"
    permission_denied_message = "休団申請の閲覧権限がありません。"
    paginate_by = 10

    def get_queryset(self):
        return LeaveApplication.objects.filter(tenant=self.request.user.tenant).order_by("-end_date")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = self.get_queryset().count()
        context['model'] = self.model._meta.verbose_name
        context['add_url'] = reverse("user:leave_application_create")
        context['list_display_fields'] = self.list_display_fields
        context['detail_url_field'] = self.detail_url_field
        return context


# 休団申請の詳細ビュー
class LeaveApplicationDetailView(LoginRequiredMixin, OrchestraPermissionRequiredMixin, TemplateView):
    template_name = "user/leave_application_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        leave_application_id = self.kwargs.get('pk')
        context['leave_application'] = LeaveApplication.objects.get(object_id=leave_application_id, tenant=self.request.user.tenant)
        return context


# 休団申請の削除ビュー
class LeaveApplicationDeleteView(LoginRequiredMixin, OrchestraPermissionRequiredMixin, OrchestraDeleteMixin, DeleteView):
    model = LeaveApplication
    template_name = "user/leave_application_delete.html"
    success_url = reverse_lazy("user:leave_application_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('user:leave_application_detail', kwargs={'pk': self.object.pk})
        return context


def debug_env(request):
    return HttpResponse(
        f"SCRIPT_NAME={request.META.get('SCRIPT_NAME')}<br>"
        f"PATH_INFO={request.META.get('PATH_INFO')}<br>"
        f"REQUEST_URI={request.META.get('REQUEST_URI')}"
    )