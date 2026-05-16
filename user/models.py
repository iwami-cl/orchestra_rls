import uuid
import django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from instrument.models import Instrument
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import Permission
from .permission_settings import DEFAULT_PERMISSION_PRESETS


# Create your models here.
class Tenant(models.Model):
    class Meta:
        db_table = 'tenants'
        verbose_name = 'テナント'
        verbose_name_plural = 'テナント'

    tenant_id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    realm = models.CharField(max_length=255, unique=True, verbose_name="団体コード")  # 半角英数字とハイフンのみのコード
    name = models.CharField(max_length=255, verbose_name="団体名")

    def __str__(self):
        return self.name
    
    def set_default_permissions(self):
        # デフォルトのパーミッションプリセットをテナントに挿入する
        for preset in DEFAULT_PERMISSION_PRESETS:
            preset_obj, created = PermissionPreset.objects.get_or_create(
                tenant=self,
                name=preset['name']
            )
            if created:
                for perm_codename in preset['permissions']:
                    try:
                        custom_perm = CustomPermission.objects.get(permission__codename=perm_codename)
                        preset_obj.permissions.add(custom_perm)
                    except CustomPermission.DoesNotExist:
                        continue
                preset_obj.save()
            
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding  # オブジェクトが新規作成されるかどうかを判定
        super().save(*args, **kwargs)  # まずは保存してIDを生成
        if is_new:
            self.set_default_permissions()  # 新規作成された場合にデフォルトのパーミッションを設定


class TenantUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理者'),
        ('member', 'メンバー'),
        ('guest', 'ゲスト'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member', verbose_name="ロール")

    user_id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True)
    instrument = models.ForeignKey(Instrument, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="担当楽器")
    display_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="ニックネーム")

    def __str__(self):
        name = self.display_name if self.display_name else self.get_full_name()
        return name
    
    def get_display_name(self):
        if self.display_name:
            return self.display_name
        return self.get_full_name()
    
    def get_full_name(self):
        full_name = self.username
        if self.first_name or self.last_name:
            full_name = f"{self.last_name} {self.first_name}"
        return full_name.strip()
    
    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, '不明な役割')
    
    def is_admin(self):
        return self.role == 'admin'

    def is_member(self):
        return self.role == 'member'

    def is_guest(self):
        return self.role == 'guest'
    
    def get_detail_url(self):
        return reverse('user:user_detail', args=[self.pk])

    class Meta:
        db_table = 'tenant_users'
        verbose_name = '団員'
        verbose_name_plural = '団員'


def get_after_30_days():
    return now() + timedelta(days=30)


class UserActivateTokens(models.Model):

    class Meta:
        db_table = 'user_activate_tokens'
        verbose_name = 'ユーザーアクティベートトークン'
        verbose_name_plural = 'ユーザーアクティベートトークン'

    token_id = models.BigAutoField("ID", primary_key=True)
    user = models.OneToOneField(TenantUser, on_delete=models.CASCADE)
    activate_token = models.UUIDField(unique=True)
    expiration_date = models.DateTimeField(default=get_after_30_days)
    created_at = models.DateTimeField(auto_now_add=True)
    reset_count_for_today = models.IntegerField(default=0)

    @classmethod
    def activate_user_by_token(cls, token):
        try:
            user_token = cls.objects.get(activate_token=token)
            if user_token.expiration_date < now():
                return False  # トークンが期限切れ
            user = user_token.user
            user.is_active = True
            user.save()
            user_token.delete()  # トークンは一度使用したら削除
            return True
        except cls.DoesNotExist:
            return False  # トークンが存在しない場合


# Djangoのパーミッションをアプリ向けにカスタム
class CustomPermission(models.Model):
    permission = models.OneToOneField(Permission, on_delete=models.CASCADE, primary_key=True, related_name='custom_permission')
    display_name = models.CharField(max_length=255)
    private = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'custom_permissions'
        verbose_name = 'カスタムパーミッション'
        verbose_name_plural = 'カスタムパーミッション'

    def __str__(self):
        if self.display_name:
            return self.display_name
        return str(self.permission)


""" 
パーミッションのプリセットを定義
パーミッションのプリセットは、テナントごとに異なる権限セットを簡単に割り当てるためのものです。
"""
class PermissionPreset(models.Model):
    name = models.CharField(max_length=50, unique=False)
    permissions = models.ManyToManyField(CustomPermission, related_name='presets')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        db_table = 'permission_presets'
        verbose_name = 'パーミッションプリセット'
        verbose_name_plural = 'パーミッションプリセット'

    def __str__(self):
        return self.tenant.name + ' - ' + self.name



# 休団者管理テーブル
class LeaveApplication(models.Model):
    object_id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(TenantUser, on_delete=models.CASCADE, verbose_name="ユーザー")
    start_date = models.DateField(verbose_name="開始日")
    end_date = models.DateField(verbose_name="終了日")
    reason = models.TextField(max_length=20000, blank=True, null=True, verbose_name="理由")
    is_approved = models.BooleanField(default=False, verbose_name="承認済み")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True, verbose_name="テナント")

    class Meta:
        db_table = 'leave_applications'
        verbose_name = '休団申請'
        verbose_name_plural = '休団申請'

    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date}"
    
    def get_detail_url(self):
        return reverse('user:leave_application_detail', args=[self.pk])