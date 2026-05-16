from conftest import BASE_URL, driver, login_as, logout
from selenium.webdriver.common.by import By
from user import models as user_models
from music import models as music_models
from schedule import models as schedule_models
import datetime
import pytest
import time

# 実行コマンド: pytest -v selenium/TC-SCHEDULE/01_schedule_create_test.py
@pytest.fixture(autouse=True)
def reset_browser_state(driver):
    # このファイルではクラス単位でログイン状態を維持するため、クッキーは消さずに画面遷移のみ行う。
    driver.get(BASE_URL)
    yield
    driver.get(BASE_URL)


class TestCreateScheduleNoLogin:
    def test_no_login_access(self, driver):
        # 未ログイン状態を明示的に作る
        driver.get(BASE_URL)
        driver.delete_all_cookies()

        # 未ログイン状態でスケジュール作成ページにアクセスできないこと（ログインページにリダイレクトされること）
        driver.get(f"{BASE_URL}/schedule/schedule/create/")
        assert driver.current_url.startswith(f"{BASE_URL}/user/login/"), "未ログインユーザーはスケジュール作成ページにアクセスできず、ログインページにリダイレクトされる必要があります。"


class TestCreateSchedule:
    @pytest.fixture(scope="class", autouse=True)
    def login_once(self, request, driver):
        user = user_models.TenantUser.objects.first()
        if user is None:
            raise Exception("No test user found in the database. Please create a test user before running this test.")

        login_as(driver, user.username)
        request.cls.login_user = user
        yield
        logout(driver)

    def test_create_schedule_form(self, driver):
        user = self.login_user
        
        # 権限付与
        perm = user_models.CustomPermission.objects.get(permission__codename="add_schedule")
        user.user_permissions.add(perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)
        # スケジュール作成ページにアクセスする
        driver.get(f"{BASE_URL}/schedule/schedule/create/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/create/", "スケジュール作成ページにアクセスできる必要があります。"
        
        # 入力欄の確認
        title_input = driver.find_elements(By.NAME, "title")
        assert len(title_input) == 1, "認証済みユーザーにはタイトル入力欄が表示される必要があります。"
        
        date_input = driver.find_elements(By.NAME, "date")
        assert len(date_input) == 1, "認証済みユーザーには日付入力欄が表示される必要があります。"

        # 今日の日付が初期値として入っていることを確認する
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        assert date_input[0].get_attribute("value") == today_str, "日付入力欄の初期値が今日の日付である必要があります。"
        
        start_input = driver.find_elements(By.NAME, "start")
        assert len(start_input) == 1, "認証済みユーザーには開始時刻入力欄が表示される必要があります。"
        
        end_input = driver.find_elements(By.NAME, "end")
        assert len(end_input) == 1, "認証済みユーザーには終了時刻入力欄が表示される必要があります。"

        place_input = driver.find_elements(By.NAME, "place")
        assert len(place_input) == 1, "認証済みユーザーには場所入力欄が表示される必要があります。"
        
        map_input = driver.find_elements(By.NAME, "place_map_url")
        assert len(map_input) == 1, "認証済みユーザーには地図入力欄が表示される必要があります。"

        note_input = driver.find_elements(By.NAME, "note")
        assert len(note_input) == 1, "認証済みユーザーには説明入力欄が表示される必要があります。"
        
        music_choices = driver.find_elements(By.ID, "id_music")
        assert len(music_choices) == 1, "認証済みユーザーには音楽選択欄が表示される必要があります。"

        # 楽曲の選択肢の確認(子要素を取得して、楽曲テーブルの件数と同じか確認する)
        music_options = music_choices[0].find_elements(By.XPATH, "./*")
        music_count = music_models.Music.objects.filter(end_date__gte=datetime.date.today(), tenant=user.tenant).count()
        assert len(music_options) == music_count, "楽曲選択欄の件数が楽曲テーブルの件数と一致する必要があります。"
    
    def test_no_permission_access(self, driver):
        # 権限のないユーザーでログインしてスケジュール作成ページにアクセスした場合、アクセスできないこと（スケジュール一覧ページにリダイレクトされること）
        user = self.login_user
        
        # 権限変更(スケジュール作成権限を剥奪して、スケジュール閲覧権限を付与する)
        add_perm = user_models.CustomPermission.objects.get(permission__codename="add_schedule")
        user.user_permissions.remove(add_perm.permission)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.add(view_perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/create/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "権限のないユーザーはスケジュール作成ページにアクセスできず、スケジュール一覧ページにリダイレクトされる必要があります。"

        # 権限変更(スケジュール閲覧権限を剥奪する)
        user.user_permissions.remove(view_perm.permission)
        user.save()

        driver.get(f"{BASE_URL}/schedule/schedule/create/")
        assert driver.current_url.startswith(f"{BASE_URL}/"), "スケジュール閲覧権限のないユーザーはスケジュール作成ページにアクセスできず、ホームページにリダイレクトされる必要があります。"
    
    def test_has_permission_access(self, driver):
        # 権限のあるユーザーでログインしてスケジュール作成ページにアクセスした場合、アクセスできること
        user = self.login_user
        
        # 権限変更(スケジュール作成権限を付与する)
        add_perm = user_models.CustomPermission.objects.get(permission__codename="add_schedule")
        user.user_permissions.add(add_perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/create/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/create/", "権限のあるユーザーはスケジュール作成ページにアクセスできる必要があります。"
    
    def create_schedule_helper(self, driver, input_data, should_succeed=True, expected_error=None):
        # スケジュール作成フォームに必要な情報を入力して、スケジュールが作成されること
        user = self.login_user
        
        # 権限変更(スケジュール作成権限を付与する)
        add_perm = user_models.CustomPermission.objects.get(permission__codename="add_schedule")
        user.user_permissions.add(add_perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/create/")
        
        # フォームに入力する
        title_input = driver.find_element(By.NAME, "title")
        title_input.send_keys(input_data["title"])

        date_input = driver.find_element(By.NAME, "date")
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            date_input,
            input_data["date"],
        )

        start_input = driver.find_element(By.NAME, "start")
        start_input.send_keys(input_data["start"])

        end_input = driver.find_element(By.NAME, "end")
        end_input.send_keys(input_data["end"])

        place_input = driver.find_element(By.NAME, "place")
        place_input.send_keys(input_data["place"])

        map_input = driver.find_element(By.NAME, "place_map_url")
        map_input.send_keys(input_data["place_map_url"])

        note_input = driver.find_element(By.NAME, "note")
        note_input.send_keys(input_data["note"])

        # 一番下までスクロールする
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # スクロール後の描画を待つ

        for i in range(0, input_data["music_index"]):
            check_button = driver.find_element(By.ID, f"id_music_{i}")  # 最初の楽曲を選択する
            check_button.click()

        # フォームを送信する
        submit_button = driver.find_element(By.ID, "btn-submit")
        submit_button.click()

        time.sleep(1)  # 送信後の処理を待つ

        if should_succeed:
            # スケジュール一覧ページにリダイレクトされること
            assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール作成後はスケジュール一覧ページにリダイレクトされる必要があります。"
            schedule_object = schedule_models.Schedule.objects.filter(title=input_data["title"], tenant=user.tenant).first()
            return schedule_object

        # バリデーションエラー時は作成ページに留まり、期待するエラーが表示されること
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/create/", "バリデーションエラー時はスケジュール作成ページに留まる必要があります。"
        error_message = driver.find_element(By.CLASS_NAME, "errorlist").text
        assert expected_error in error_message, f"想定したエラーメッセージが表示される必要があります: {expected_error}"

    @pytest.mark.parametrize(
        "title, should_succeed, expected_error",
        [
            pytest.param("テストスケジュール", True, None, id="normal_string"),
            pytest.param("", False, "このフィールドは必須です。", id="empty_string"),
            pytest.param("A" * 255, True, None, id="max_length_255"),
            pytest.param("A" * 256, False, "この値は 255 文字以下でなければなりません", id="over_max_length_256"),
            pytest.param("!@#$%^&*()_+-=[]{};':\",./<>?", True, None, id="special_characters"),
            pytest.param("<script>alert('xss')</script>", True, None, id="xss_payload"),
            pytest.param("' OR '1'='1' --", True, None, id="sql_injection_payload"),
            pytest.param("  前後空白  ", True, None, id="trim_target_string"),
            pytest.param("\\n\\t\\r\\\"\\'\\\\", True, None, id="escape_characters"),
            pytest.param("𠮷野家", True, None, id="surrogate_pair"),
            pytest.param("テスト😀", True, None, id="emoji"),
            pytest.param("テストSchedule", True, None, id="multilingual_jp_en"),
            pytest.param("1行目\n2行目", True, None, id="newline"),
            pytest.param("タイトル\tタブ", True, None, id="tab"),
        ],
    )
    def test_title_validation(self, driver, title, should_succeed, expected_error):
        # test_plan.md の「文字列入力」パターンのみを title バリデーションで確認する。
        input_data = {
            "title": title,
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "start": "10:00",
            "end": "12:00",
            "place": "練習場所",
            "place_map_url": "https://maps.app.goo.gl/tTqFEw8jFXhvokyA6",
            "note": "説明文",
            "music_index": 1,
        }
        schedule = self.create_schedule_helper(
            driver,
            input_data,
            should_succeed=should_succeed,
            expected_error=expected_error,
        )

        # 作成成功した場合、スケジュールのタイトルが正しく保存されていること
        if should_succeed:
            assert schedule is not None, "スケジュールが作成されている必要があります。"
            assert schedule.title == title, "スケジュールのタイトルが正しく保存されている必要があります。"
        
        # 後処理
        if schedule is not None:
            schedule.delete()

class TestCreateScheduleAdmin:
    @pytest.fixture(scope="class", autouse=True)
    def login_once_admin(self, request, driver):
        admin_user = user_models.TenantUser.objects.filter(role="admin").first()
        if admin_user is None:
            raise Exception("No admin user found in the database. Please create an admin user before running this test.")

        login_as(driver, admin_user.username)
        request.cls.admin_user = admin_user
        yield
        logout(driver)

    def test_admin_access(self, driver):
        # adminユーザーでログインしてスケジュール作成ページにアクセスした場合、アクセスできること
        admin_user = self.admin_user

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/create/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/create/", "adminユーザーはスケジュール作成ページにアクセスできる必要があります。"