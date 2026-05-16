from conftest import BASE_URL, driver, login_as, logout
from selenium.webdriver.common.by import By
from user import models as user_models
from music import models as music_models
from schedule import models as schedule_models
import datetime
import pytest

# 実行コマンド: pytest -v selenium/TC-SCHEDULE/03_schedule_update_test.py
@pytest.fixture(autouse=True)
def reset_browser_state(driver):
    # このファイルではクラス単位でログイン状態を維持するため、クッキーは消さずに画面遷移のみ行う。
    driver.get(BASE_URL)
    yield
    driver.get(BASE_URL)


class TestUpdateScheduleNoLogin:
    def test_no_login_access(self, driver):
        # 未ログイン状態を明示的に作る
        driver.get(BASE_URL)
        driver.delete_all_cookies()

        # 未ログイン状態でスケジュール編集ページにアクセスできないこと（ログインページにリダイレクトされること）
        user = user_models.TenantUser.objects.first()
        if user is None:
            raise Exception("No test user found in the database. Please create a test user before running this test.")

        schedule = schedule_models.Schedule.objects.filter(tenant=user.tenant).first()
        if schedule is None:
            raise Exception("No schedule found in the database. Please create a schedule before running this test.")

        driver.get(f"{BASE_URL}/schedule/schedule/change/{schedule.id}")
        assert driver.current_url.startswith(f"{BASE_URL}/user/login/"), "未ログインユーザーはスケジュール編集ページにアクセスできず、ログインページにリダイレクトされる必要があります。"


class TestUpdateSchedule:
    @pytest.fixture(scope="class", autouse=True)
    def login_once(self, request, driver):
        user = user_models.TenantUser.objects.first()
        if user is None:
            raise Exception("No test user found in the database. Please create a test user before running this test.")

        login_as(driver, user.username)
        request.cls.login_user = user
        yield
        logout(driver)

    def test_update_schedule_form(self, driver):
        user = self.login_user

        # スケジュールを用意する
        schedule = schedule_models.Schedule.objects.filter(tenant=user.tenant).first()
        if schedule is None:
            raise Exception("No schedule found in the database. Please create a schedule before running this test.")

        # 権限付与
        perm = user_models.CustomPermission.objects.get(permission__codename="change_schedule")
        user.user_permissions.add(perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)

        # スケジュール編集ページにアクセスする
        driver.get(f"{BASE_URL}/schedule/schedule/change/{schedule.id}")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/change/{schedule.id}", "スケジュール編集ページにアクセスできる必要があります。"

        # 入力欄の確認
        title_input = driver.find_elements(By.NAME, "title")
        assert len(title_input) == 1, "認証済みユーザーにはタイトル入力欄が表示される必要があります。"

        # 既存のタイトルが初期値として入っていることを確認する
        assert title_input[0].get_attribute("value") == schedule.title, "タイトル入力欄の初期値が既存のスケジュールのタイトルである必要があります。"

        date_input = driver.find_elements(By.NAME, "date")
        assert len(date_input) == 1, "認証済みユーザーには日付入力欄が表示される必要があります。"

        # 既存の日付が初期値として入っていることを確認する
        assert date_input[0].get_attribute("value") == schedule.date.strftime("%Y-%m-%d"), "日付入力欄の初期値が既存のスケジュールの日付である必要があります。"

        start_input = driver.find_elements(By.NAME, "start")
        assert len(start_input) == 1, "認証済みユーザーには開始時刻入力欄が表示される必要があります。"

        # 既存の開始時刻が初期値として入っていることを確認する
        assert start_input[0].get_attribute("value") == schedule.start.strftime("%H:%M"), "開始時刻入力欄の初期値が既存のスケジュールの開始時刻である必要があります。"

        end_input = driver.find_elements(By.NAME, "end")
        assert len(end_input) == 1, "認証済みユーザーには終了時刻入力欄が表示される必要があります。"

        # 既存の終了時刻が初期値として入っていることを確認する
        assert end_input[0].get_attribute("value") == schedule.end.strftime("%H:%M"), "終了時刻入力欄の初期値が既存のスケジュールの終了時刻である必要があります。"

        place_input = driver.find_elements(By.NAME, "place")
        assert len(place_input) == 1, "認証済みユーザーには場所入力欄が表示される必要があります。"

        # 既存の場所が初期値として入っていることを確認する
        assert place_input[0].get_attribute("value") == (schedule.place or ""), "場所入力欄の初期値が既存のスケジュールの場所である必要があります。"

        map_input = driver.find_elements(By.NAME, "place_map_url")
        assert len(map_input) == 1, "認証済みユーザーには地図入力欄が表示される必要があります。"

        # 既存の地図URLが初期値として入っていることを確認する
        assert map_input[0].get_attribute("value") == (schedule.place_map_url or ""), "地図入力欄の初期値が既存のスケジュールの地図URLである必要があります。"

        note_input = driver.find_elements(By.NAME, "note")
        assert len(note_input) == 1, "認証済みユーザーには説明入力欄が表示される必要があります。"

        # 既存の説明が初期値として入っていることを確認する
        assert note_input[0].get_attribute("value") == (schedule.note or ""), "説明入力欄の初期値が既存のスケジュールの説明である必要があります。"

        music_choices = driver.find_elements(By.ID, "id_music")
        assert len(music_choices) == 1, "認証済みユーザーには音楽選択欄が表示される必要があります。"

        # 楽曲の選択肢の確認(子要素を取得して、楽曲テーブルの件数と同じか確認する)
        music_options = music_choices[0].find_elements(By.XPATH, "./*")
        music_count = music_models.Music.objects.filter(end_date__gte=datetime.date.today(), tenant=user.tenant).count()
        assert len(music_options) == music_count, "楽曲選択欄の件数が楽曲テーブルの件数と一致する必要があります。"

        # 既存の楽曲が選択済みであることを確認する
        selected_option_ids = {
            opt.get_attribute("value")
            for opt in music_options
            if opt.get_attribute("selected") is not None
        }
        expected_music_ids = set(str(m.id) for m in schedule.music.all())
        assert selected_option_ids == expected_music_ids, "楽曲選択欄の選択済み楽曲が既存のスケジュールの楽曲と一致する必要があります。"

    def test_no_permission_access(self, driver):
        # 権限のないユーザーでログインしてスケジュール編集ページにアクセスした場合、アクセスできないこと（スケジュール詳細ページにリダイレクトされること）
        user = self.login_user

        schedule = schedule_models.Schedule.objects.filter(tenant=user.tenant).first()
        if schedule is None:
            raise Exception("No schedule found in the database. Please create a schedule before running this test.")

        # 権限変更(スケジュール編集権限を剥奪して、スケジュール閲覧権限を付与する)
        change_perm = user_models.CustomPermission.objects.get(permission__codename="change_schedule")
        user.user_permissions.remove(change_perm.permission)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.add(view_perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/change/{schedule.id}")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/detail/{schedule.id}", "権限のないユーザーはスケジュール編集ページにアクセスできず、スケジュール詳細ページにリダイレクトされる必要があります。"

        # 権限変更(スケジュール閲覧権限を剥奪する)
        user.user_permissions.remove(view_perm.permission)
        user.save()

        driver.get(f"{BASE_URL}/schedule/schedule/change/{schedule.id}")
        assert driver.current_url.startswith(f"{BASE_URL}/"), "スケジュール閲覧権限のないユーザーはスケジュール編集ページにアクセスできず、ホームページにリダイレクトされる必要があります。"

    def test_has_permission_access(self, driver):
        # 権限のあるユーザーでログインしてスケジュール編集ページにアクセスした場合、アクセスできること
        user = self.login_user

        schedule = schedule_models.Schedule.objects.filter(tenant=user.tenant).first()
        if schedule is None:
            raise Exception("No schedule found in the database. Please create a schedule before running this test.")

        # 権限変更(スケジュール編集権限を付与する)
        change_perm = user_models.CustomPermission.objects.get(permission__codename="change_schedule")
        user.user_permissions.add(change_perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/change/{schedule.id}")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/change/{schedule.id}", "権限のあるユーザーはスケジュール編集ページにアクセスできる必要があります。"


class TestUpdateScheduleAdmin:
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
        # adminユーザーでログインしてスケジュール編集ページにアクセスした場合、アクセスできること
        admin_user = self.admin_user

        schedule = schedule_models.Schedule.objects.filter(tenant=admin_user.tenant).first()
        if schedule is None:
            raise Exception("No schedule found in the database. Please create a schedule before running this test.")

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/change/{schedule.id}")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/change/{schedule.id}", "adminユーザーはスケジュール編集ページにアクセスできる必要があります。"
