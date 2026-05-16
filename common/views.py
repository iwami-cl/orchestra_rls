from django.shortcuts import resolve_url

from django.shortcuts import redirect, render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse

from django.contrib import messages
from django.http import Http404


# Create your views here.
class OrchestraPermissionRequiredMixin(PermissionRequiredMixin):
    permission_required = None

    # ① URL（例: "/schedule/schedule/list/"）
    permission_redirect_url = None

    # ② URL kwargs（例: {"pk": "some-id"}）
    permission_redirect_url_kwargs = None

    permission_denied_message = "権限がありません。"

    # ③ 完全に動的に URL を返す関数
    #    def get_permission_redirect_url(self, request, *args, **kwargs):
    #        return "/custom/url/"
    
    def get_permission_redirect_url(self, request, *args, **kwargs):
        """
        3段階で URL を決定する:
        1. 動的メソッドがあればそれを使う
        2. URL 名 + kwargs で reverse する
        3. それもなければデフォルト
        """
        # ③ 動的メソッドがオーバーライドされていれば優先
        if hasattr(self, "permission_redirect_url") and callable(self.permission_redirect_url):
            return self.permission_redirect_url(request, *args, **kwargs)

        # ② URL + kwargs
        if self.permission_redirect_url:
            kwargs = self.permission_redirect_url_kwargs or {}
            if kwargs:
                return self.permission_redirect_url + "?" + "&".join([f"{key}={value}" for key, value in kwargs.items()])
            return self.permission_redirect_url

        # ① デフォルト
        return resolve_url("index")

    def dispatch(self, request, *args, **kwargs):
        # 未ログイン
        if not request.user.is_authenticated:
            return redirect(self.get_login_url())
        
        # adminユーザーは全ての権限を持つ
        if request.user.is_admin():
            return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)

        # 権限不足
        if self.permission_required and not request.user.has_perm(self.permission_required):
            url = self.get_permission_redirect_url(request, *args, **kwargs)
            messages.error(request, self.permission_denied_message)
            return redirect(url)

        return super().dispatch(request, *args, **kwargs)


class OrchestraDeleteMixin:
    not_found_message = "削除対象が存在しません。"

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            messages.error(self.request, self.not_found_message)
            return None

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return redirect(self.get_safe_success_url())
        return super().dispatch(request, *args, **kwargs)
    
    def get_safe_success_url(self):
        """
        DeleteView の危険な format() を絶対に通さない安全な URL を返す
        """
        return resolve_url(self.success_url)