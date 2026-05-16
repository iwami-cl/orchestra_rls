import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from user import models as user_models

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/user/login/"

TEST_URLS = {
    "index": {"url": f"{BASE_URL}/", "expected": "redirect_to_login"},
    #"admin": {"url": f"{BASE_URL}/admin/", "expected": "redirect_to_login"},
    #"tenant_update": {"url": f"{BASE_URL}/tenant/{{uuid_pk}}/", "expected": "redirect_to_login"},

    # # user.urls
    "login": {"url": LOGIN_URL, "expected": "ok"},
    # #"logout": {"url": f"{BASE_URL}/user/logout/", "expected": "redirect_to_login"},
    "create_tenant": {"url": f"{BASE_URL}/user/create_tenant/", "expected": "ok"},
    # "password_reset": {"url": f"{BASE_URL}/user/password_reset?user_id={{uuid_pk}}", "expected": "ok", "model": user_models.TenantUser},
    "password_reset_success": {"url": f"{BASE_URL}/user/password_reset/success/", "expected": "ok"},
    "password_reset_activate": {"url": f"{BASE_URL}/user/password_reset/activate/", "expected": "ok"},
    "user_list": {"url": f"{BASE_URL}/user/user/list/", "expected": "redirect_to_login"},
    "user_detail": {"url": f"{BASE_URL}/user/user/{{uuid_pk}}/detail/", "expected": "redirect_to_login", "model": user_models.TenantUser},
    "user_delete": {"url": f"{BASE_URL}/user/user/{{uuid_pk}}/delete/", "expected": "redirect_to_login", "model": user_models.TenantUser},
    # "terms_of_service": {"url": f"{BASE_URL}/user/terms_of_service/", "expected": "redirect_to_login"},
    "leave_application_create": {"url": f"{BASE_URL}/user/leave_application/create/", "expected": "redirect_to_login"},
    "leave_application_update": {"url": f"{BASE_URL}/user/leave_application/{{uuid_pk}}/update/", "expected": "redirect_to_login", "model": user_models.LeaveApplication},
    "leave_application_list": {"url": f"{BASE_URL}/user/leave_application/list/", "expected": "redirect_to_login"},
    "leave_application_detail": {"url": f"{BASE_URL}/user/leave_application/{{uuid_pk}}/detail/", "expected": "redirect_to_login", "model": user_models.LeaveApplication},
    "leave_application_delete": {"url": f"{BASE_URL}/user/leave_application/{{uuid_pk}}/delete/", "expected": "redirect_to_login", "model": user_models.LeaveApplication},

    # # music.urls
    "music_create": {"url": f"{BASE_URL}/music/create/", "expected": "redirect_to_login"},
    # "music_update": {"url": f"{BASE_URL}/music/update/{{int_pk}}", "expected": "redirect_to_login"},
    # "music_delete": {"url": f"{BASE_URL}/music/delete/{{int_pk}}", "expected": "redirect_to_login"},
    # "music_detail": {"url": f"{BASE_URL}/music/detail/{{int_pk}}", "expected": "redirect_to_login"},
    "music_list": {"url": f"{BASE_URL}/music/list/", "expected": "redirect_to_login"},
    # "formation_create": {"url": f"{BASE_URL}/music/detail/{{int_pk}}/formation_create/", "expected": "redirect_to_login"},
    # "formation_update": {"url": f"{BASE_URL}/music/detail/{{int_pk}}/formation_update/{{uuid_formation_id}}", "expected": "redirect_to_login"},
    # "formation_delete": {"url": f"{BASE_URL}/music/detail/{{int_pk}}/formation_delete/{{uuid_formation_id}}", "expected": "redirect_to_login"},

    # # schedule.urls
    # "schedule_update": {"url": f"{BASE_URL}/schedule/schedule/change/{{uuid_pk}}", "expected": "redirect_to_login"},
    "schedule_create": {"url": f"{BASE_URL}/schedule/schedule/create/", "expected": "redirect_to_login"},
    # "schedule_detail": {"url": f"{BASE_URL}/schedule/schedule/detail/{{uuid_pk}}", "expected": "redirect_to_login"},
    "schedule_list": {"url": f"{BASE_URL}/schedule/schedule/list/", "expected": "redirect_to_login"},
    # "schedule_delete": {"url": f"{BASE_URL}/schedule/schedule/delete/{{uuid_pk}}", "expected": "redirect_to_login"},

    # # schedule.api.urls
    #"api_schedule_list": {"url": f"{BASE_URL}/api/schedule/schedule_list/", "expected": "redirect_to_login"},
    # "api_post_attendance": {"url": f"{BASE_URL}/api/schedule/post_attendance/", "expected": "redirect_to_login"},

    # # instrument.urls
    "instrument_part_list": {"url": f"{BASE_URL}/instrument/parts/", "expected": "redirect_to_login"},
    # "instrument_part_detail": {"url": f"{BASE_URL}/instrument/parts/{{uuid_pk}}/detail/", "expected": "redirect_to_login"},
    "instrument_part_create": {"url": f"{BASE_URL}/instrument/parts/create/", "expected": "redirect_to_login"},
    # "instrument_part_update": {"url": f"{BASE_URL}/instrument/parts/{{uuid_pk}}/update/", "expected": "redirect_to_login"},
    # "instrument_part_delete": {"url": f"{BASE_URL}/instrument/parts/{{uuid_pk}}/delete/", "expected": "redirect_to_login"},
}

# pytestのテストクラスを定義
# 実行コマンド: pytest -v selenium/TC-LOGIN/login_test.py
class TestLogin:
    @staticmethod
    def _resolve_url(value):
        url = value["url"]

        if "model" in value:
            model = value["model"]
            instance = model.objects.first()
            if instance is None:
                return None
            print(url.replace("{uuid_pk}", str(instance.pk)))
            return url.replace("{uuid_pk}", str(instance.pk))

        if "{{int_pk}}" in url:
            return url.replace("{{int_pk}}", "1")

        if "{{uuid_formation_id}}" in url:
            return url.replace("{{uuid_formation_id}}", "00000000-0000-0000-0000-000000000000")

        return url

    def test_login(self, driver):
        # ログインテストの実装
        driver.get(LOGIN_URL)
        assert driver.current_url.startswith(LOGIN_URL)

    def test_access_control(self, driver):
        # 未ログイン時のアクセス制限テストの実装
        for key, value in TEST_URLS.items():
            expected = value["expected"]

            url = self._resolve_url(value)
            if url is None:
                model_name = value["model"].__name__
                print(f"Warning: No instance found for {model_name}, skipping {key} test.")
                continue

            print(f"Getting {url}...")
            driver.get(url)

            if expected == "redirect_to_login":
                # ログイン画面にリダイレクトされることを確認
                assert driver.current_url.startswith(LOGIN_URL), f"Expected to be redirected to login for {key}, but got {driver.current_url}"
            elif expected == "ok":
                # 正常にアクセスできることを確認
                assert driver.current_url == url, f"Expected to access {url} for {key}, but got {driver.current_url}"
    