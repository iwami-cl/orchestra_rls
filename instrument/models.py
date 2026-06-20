import uuid
from django.db import models


# Create your models here.
class Instrument(models.Model):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="楽器名")
    initial = models.CharField(max_length=255, null=True, blank=False, verbose_name="イニシャル")
    jp_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="日本語名")
    order = models.IntegerField(null=False, blank=False, default=0, verbose_name="表示順")

    tenant = models.ForeignKey('user.Tenant', on_delete=models.CASCADE, null=False, blank=False, verbose_name="テナント")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tenant_instrument'
        verbose_name = 'Tenant Instrument'
        verbose_name_plural = 'Tenant Instrument'


class InstrumentPart(models.Model):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    instrument = models.ManyToManyField(Instrument, blank=False, verbose_name="楽器")
    part_name = models.CharField(max_length=255, null=False, blank=False, verbose_name="パート名")

    tenant = models.ForeignKey('user.Tenant', on_delete=models.CASCADE, null=False, blank=False, verbose_name="テナント")

    owner = models.ForeignKey('user.TenantUser', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所有者")

    def __str__(self):
        return self.part_name
    
    # # ownerのバリデーション
    # def clean(self):
    #     from django.core.exceptions import ValidationError

    #     # テナントと所有者のテナントが一致するか確認
    #     if self.owner and self.owner.tenant != self.tenant:
    #         raise ValidationError("このユーザーはテナントに所属していないため設定できません。")

    class Meta:
        db_table = 'tenant_instrument_part'
        verbose_name = 'パート'
        verbose_name_plural = 'パート'