"""
URL configuration for orchestra_rls project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from orchestra_rls import settings
from user.views import IndexView, TenantUpdateView, debug_env, introduce
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', introduce, name='introduce'),
    path('admin/', admin.site.urls),
    path('otonosu/user/', include("user.urls")),
    path('otonosu/home/', IndexView.as_view(), name="index"),
    path('otonosu/music/', include("music.urls")),
    path('otonosu/schedule/', include("schedule.urls")),
    path('otonosu/api/schedule/', include("schedule.api.urls")),
    path('otonosu/tenant/<uuid:pk>/', TenantUpdateView.as_view(), name='tenant_update'),  # 追加
    path('otonosu/instrument/', include("instrument.urls")),  # 追加
    #path('debug-env/', debug_env),
    #path('otonosu/api/notification/', include("notification.api.urls")),  # 追加
    #path('otonosu/stripe/', include("stripe.urls")),  # 追加
]

#urlpatterns += staticfiles_urlpatterns()
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)