from datetime import timedelta
from django.utils import timezone
import uuid
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import CustomPermission, LeaveApplication, Tenant, TenantUser, UserActivateTokens, PermissionPreset

class SignUpForm(UserCreationForm):
    class Meta:
        model = TenantUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )


# ログインフォームを追加
class LoginFrom(AuthenticationForm):
    class Meta:
        model = TenantUser


class TenantSignUpForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text="必須。150文字以内。英数字と @/./+/-/_ のみ使用できます。",
        label="ユーザー名"
    )
    email = forms.EmailField(
        required=True,
        label="メールアドレス",
        help_text="必須。メールアドレスを入力してください。"
        )
    first_name = forms.CharField(max_length=30, label="名")
    last_name = forms.CharField(max_length=30, label="姓")
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label="パスワード")
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="パスワード（確認）")
    tenant_name = forms.CharField(max_length=100, required=True, label="団体名")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "パスワードが一致しません。")
        return cleaned_data

    def save(self, commit=True):
        if commit:
            with transaction.atomic():
                # Tenantの作成
                tenant = Tenant.objects.create(name=self.cleaned_data["tenant_name"], realm=self.cleaned_data["tenant_name"].lower().replace(" ", "_"))
                tenant.save()

                # TenantUserの作成
                new_user = TenantUser.objects.create(
                    username=self.cleaned_data["username"],
                    email=self.cleaned_data["email"],
                    first_name=self.cleaned_data["first_name"],
                    last_name=self.cleaned_data["last_name"],
                    role='admin',  # サインアップしたユーザーは自動的にadminロールになる
                    is_active=True,
                    tenant=tenant,
                )
                new_user.set_password(self.cleaned_data["password1"])
                new_user.save()

                return new_user
        return None
    class Meta:
        model = TenantUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "tenant_name",  # テナント名フィールドがモデルにある場合
        )

# パスワードリセットフォーム
class PasswordResetForm(forms.Form):
    email = forms.EmailField(required=False, label="メールアドレス")  # ログインしていないユーザー向けのメールアドレスフィールド
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=True, label="新しいパスワード")
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="新しいパスワード（確認）")

    def __init__(self, *args, **kwargs):
        # ユーザーIDを受け取る
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)

        # ユーザーIDがある場合は、メールアドレスをFormから削除する
        if self.user_id is not None:
            self.fields.pop('email')

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error("new_password2", "新しいパスワードが一致しません。")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user_id is None:
            if not TenantUser.objects.filter(email=email).exists():
                raise forms.ValidationError("このメールアドレスは登録されていません。")
        return email
    
    def save(self, commit=True):
        user = None
        if self.user_id is None:
            email = self.cleaned_data.get('email')
            try:
                user = TenantUser.objects.get(email=email)
                self.user_id = user.pk  # ユーザーIDを設定
            except TenantUser.DoesNotExist:
                raise forms.ValidationError("このメールアドレスは登録されていません。")
        else:
            try:
                user = TenantUser.objects.get(pk=self.user_id)
            except TenantUser.DoesNotExist:
                raise forms.ValidationError("ユーザーが見つかりません。")
        new_password = self.cleaned_data["new_password1"]
        user.set_password(new_password)
        user.is_active = False  # パスワードリセット後にアクティブ化
        uat, created = UserActivateTokens.objects.get_or_create(
            user=user,
            defaults={'activate_token': uuid.uuid4()}
        )
        today = timezone.now()
        create_after_24h = uat.created_at + timedelta(hours=24)
        if not created:
            if create_after_24h > today and uat.reset_count_for_today >= 3:
                raise forms.ValidationError("本日はパスワードリセットの上限回数に達しました。明日以降に再度お試しください。")
            elif create_after_24h > today and uat.reset_count_for_today < 3:
                uat.reset_count_for_today += 1  # 今日のリセット回数を増やす
            elif create_after_24h <= today:
                uat.reset_count_for_today = 0  # リセット回数を0にリセット
                uat.created_at = timezone.now()  # 作成日時を更新
        if commit:
            user.save()
            uat.save()
        return uat
    
    class Meta:
        model = TenantUser
        fields = (
            "email",  # メールアドレスフィールドがモデルにある場合
            "new_password1",
            "new_password2",
        )


class PasswordResetForAuthenticatedForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=True, label="新しいパスワード")
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="新しいパスワード（確認）")

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error("new_password2", "新しいパスワードが一致しません。")
        return cleaned_data

    def save(self, user, commit=True):
        new_password = self.cleaned_data["new_password1"]
        user.set_password(new_password)
        if commit:
            user.save()
        return user
    
    class Meta:
        model = TenantUser
        fields = (
            "new_password1",
            "new_password2",
        )

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = (
            "name",
            "realm",
        )

# ユーザーフォーム
class UserForm(forms.ModelForm):
    has_parmision_change = False  # 権限変更の可否を制御するフラグ
    login_user = None  # ログインユーザーを保持する変数

    # 権限の選択肢を追加
    permissions = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.filter(private=False),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="権限"
    )

    def __init__(self, *args, login_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # 引数からログインユーザーの権限を取得して、permissionsフィールド有無を制御
        self.login_user = login_user
        if self.login_user and (self.login_user.has_perm("user.change_tenantuser") or self.login_user.is_admin()):
            self.has_parmision_change = True
            # 権限のチェックボックスをユーザーの現在の権限に基づいて初期化
            if self.instance and self.instance.pk:
                user_permissions = self.instance.user_permissions.values_list('id', flat=True)
                self.fields['permissions'].initial = CustomPermission.objects.filter(permission_id__in=user_permissions)


            # 権限プリセットの選択肢をテナントに基づいて動的に設定
            tenant = self.login_user.tenant
            presets = PermissionPreset.objects.filter(tenant=tenant)
            choices = [(preset.id, preset.name) for preset in presets]
            choices.insert(0, ('', '- 権限プリセットを選択 -'))  # 先頭に未選択を追加

            self.fields['permission_presets'].choices = choices
            if self.instance and self.instance.pk:
                # ユーザーの権限一覧が、権限プリセットと一致したらプリセットを選択状態にする
                user_permission_ids = set(self.instance.user_permissions.values_list('id', flat=True))
                for preset in presets:
                    preset_permission_ids = set(preset.permissions.values_list('permission_id', flat=True))
                    if user_permission_ids == preset_permission_ids:
                        self.fields['permission_presets'].initial = preset.id
                        break
        else:
            self.fields.pop('permissions')  # 権限フィールドをフォームから削除
            self.fields.pop('permission_presets')  # 権限プリセットフィールドも削除
            self.fields.pop('role')  # ロールフィールドも削除


    # 権限プリセットの選択肢を追加(fromではRLSが効かないため、ビューでフィルタリングして渡す)
    permission_presets = forms.ChoiceField(choices=[], required=False, label="権限プリセット")

    # 入力欄の表示順
    field_order = [
        "username",
        "display_name",
        "last_name",
        "first_name",
        "email",
        "instrument",
        "role",  # ロールの選択肢を表示
        "permission_presets",  # 権限プリセットの選択肢を表示
        "permissions",  # 権限の選択肢を表示
    ]

    def clean_permissions(self):
        permissions = self.cleaned_data.get('permissions')
        for perm in permissions:
            if perm.private:
                raise forms.ValidationError(f"'{perm.display_name}' はプライベートな権限のため、選択できません。")
        return permissions
    
    def clean_role(self):
        if not self.has_parmision_change:
            raise forms.ValidationError("ロールを変更する権限がありません。")

        role = self.cleaned_data.get('role')
        if role not in ['admin', 'member', 'guest']:
            raise forms.ValidationError("無効なロールが選択されました。")
        return role

    class Meta:
        model = TenantUser
        fields = (
            "username",
            "display_name",
            "last_name",
            "first_name",
            "email",
            "instrument",
            "role",  # ロールの選択肢を追加
        )

        help_texts = {
            'username': '必須。150文字以内。英数字と @/./+/-/_ のみ使用できます。',
            'instrument': '演奏曲に登録されている編成の内容は変更されません。'
        }


# 休団申請フォーム
class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = (
            "user",
            "start_date",
            "end_date",
            "reason",
        )
    
    def save(self, commit=True):
        leave_application = super().save(commit=False)
        if commit:
            leave_application.save()
        return leave_application
    
    # 開始日と終了日のバリデーション
    def valid_date(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("開始日は終了日より前の日付を選択してください。")
        return self.cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        self.valid_date()  # 日付のバリデーションを呼び出す
        return cleaned_data


# 休団申請更新フォーム
class LeaveApplicationUpdateForm(LeaveApplicationForm):
    # readonlyにするフィールドを定義
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].disabled = True  # ユーザーは変更不可
    