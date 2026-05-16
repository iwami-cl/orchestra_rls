from django.db import models
from django.urls import reverse
from instrument.models import Instrument
from user.models import Tenant, TenantUser
import uuid


# Create your models here.
class Music(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False, verbose_name="曲名")
    composer = models.CharField(max_length=255, null=True, blank=True, verbose_name="作曲者")
    arranger = models.CharField(max_length=255, null=True, blank=True, verbose_name="編曲者")
    tenant = models.ForeignKey(Tenant, null=False, blank=False, verbose_name="楽団", on_delete=models.CASCADE)
    note = models.TextField(blank=True, verbose_name='備考', max_length=20000)
    is_show = models.BooleanField(default=True, verbose_name="表示フラグ")

    def __str__(self):
        return self.title
    
    def get_detail_url(self):
        return reverse('music:music_detail', args=[self.pk])

    class Meta:
        db_table = 'tenant_music'
        verbose_name = '演奏曲'
        verbose_name_plural = '演奏曲'


class Formation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    music = models.ForeignKey(Music, null=False, blank=False, verbose_name="曲名", on_delete=models.CASCADE)
    section = models.CharField(max_length=50, null=True, blank=True, verbose_name="セクション")
    users = models.ManyToManyField(TenantUser, blank=True, verbose_name='メンバー')
    instrument = models.ForeignKey(Instrument, null=False, blank=False, verbose_name="パート", on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, null=False, blank=False, verbose_name="楽団", on_delete=models.CASCADE)

    def get_users(self):
        return "\n".join([str(u) for u in self.users.all()])

    class Meta:
        db_table = 'tenant_formation'
        verbose_name = '編成'
        verbose_name_plural = '編成'

        constraints = [
            models.UniqueConstraint(fields=['music', 'instrument', 'section'], name='unique_music_instrument_section')
        ]
