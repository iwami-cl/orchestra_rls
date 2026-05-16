from django.contrib import admin
from .models import *
# Register your models here.


class MusicAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant_id")

    def get_queryset(self, request):
        return super().get_queryset(request)


class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("name", )

    def get_queryset(self, request):
        return super().get_queryset(request)


class FormationAdmin(admin.ModelAdmin):
    list_display = ("music", "instrument", "section", "get_users")

    def get_users(self, obj):
        return ",\n".join([u.username for u in obj.users.all()])


admin.site.register(Music, MusicAdmin)
admin.site.register(Formation, FormationAdmin)
