from django.contrib import admin
from django.urls import path
from django.conf import settings            # settings.pyの変数
from django.conf.urls.static import static  # メディア表示

# App_Folderからviews.pyで定義した関数呼出
from .views import (
    stripe_webhook,
    )

urlpatterns = [                                                                             # 管理画面
    path('webhook/', stripe_webhook, name='stripe-webhook'),  # WebHookのURL
]

# メディア表示
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)