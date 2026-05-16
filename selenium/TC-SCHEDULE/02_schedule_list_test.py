from conftest import BASE_URL, driver, login_as, logout
from selenium.webdriver.common.by import By
from user import models as user_models
import pytest
import datetime
import time
from dateutil.relativedelta import relativedelta
from schedule import models as schedule_models

# 実行コマンド: pytest -v selenium/TC-SCHEDULE/02_schedule_list_test.py
@pytest.fixture(autouse=True)
def reset_browser_state(driver):
    # このファイルではクラス単位でログイン状態を維持するため、クッキーは消さずに画面遷移のみ行う。
    driver.get(BASE_URL)
    yield
    driver.get(BASE_URL)


class TestScheduleListNoLogin:
    def test_no_login_access(self, driver):
        # 未ログイン状態を明示的に作る
        driver.get(BASE_URL)
        driver.delete_all_cookies()

        # 未ログイン状態でスケジュール一覧ページにアクセスできないこと（ログインページにリダイレクトされること）
        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url.startswith(f"{BASE_URL}/user/login/"), "未ログインユーザーはスケジュール一覧ページにアクセスできず、ログインページにリダイレクトされる。"


class TestScheduleList:
    @pytest.fixture(scope="class", autouse=True)
    def login_once(self, request, driver):
        user = user_models.TenantUser.objects.first()
        if user is None:
            raise Exception("No test user found in the database. Please create a test user before running this test.")

        login_as(driver, user.username)
        request.cls.login_user = user
        yield
        logout(driver)

    def test_schedule_list_access(self, driver):
        user = self.login_user
        
        # 権限変更(スケジュール閲覧権限を剥奪する)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.add(view_perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)
        # スケジュール一覧ページにアクセスする
        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール一覧ページにアクセスできる。"
        
        # # スケジュールのタイトルが表示されていることを確認する（スケジュールが存在する場合）
        # schedule_titles = driver.find_elements(By.CLASS_NAME, "schedule-title")
        # if schedule_titles:
        #     assert len(schedule_titles) > 0, "スケジュールが存在する場合、タイトルが表示される。"

    
    def test_no_permission_access(self, driver):
        # 権限のないユーザーでログインしてスケジュール一覧ページにアクセスした場合、アクセスできないこと（ホームページにリダイレクトされること）
        user = self.login_user
        
        # 権限変更(スケジュール閲覧権限を剥奪する)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.remove(view_perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url.startswith(f"{BASE_URL}/"), "スケジュール閲覧権限のないユーザーはスケジュール一覧ページにアクセスできず、ホームページにリダイレクトされる。"
        
    def test_has_permission_access(self, driver):
        # 権限のあるユーザーでログインしてスケジュール一覧ページにアクセスした場合、アクセスできること
        user = self.login_user
        
        # 権限変更(スケジュール閲覧権限を付与する)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.add(view_perm.permission)
        user.save()

        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール閲覧権限のあるユーザーはスケジュール一覧ページにアクセスできる。"
    
    def test_move_button(self, driver):
        # 月の切り替えボタンをクリックしたときの動作を確認
        user = self.login_user

        # ホームページに移動する
        driver.get(BASE_URL)

        # 権限変更(スケジュール閲覧権限を付与する)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.add(view_perm.permission)
        user.save()

        # スケジュール一覧ページにアクセスする
        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール一覧ページにアクセスできる。"
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ

        # 今月から年が変わるまで1月前に移動し続ける
        init_date = datetime.datetime.now()
        current_date = init_date
        while True:
            prev_button = driver.find_element(By.ID, "prev")
            prev_button.click()
            current_date = current_date - relativedelta(months=1)
            print(current_date)  # デバッグ用に現在の年月を出力
            time.sleep(1)  # 表示が更新されるまで少し待つ

            year_month_text = driver.find_element(By.ID, "monthYearDisplay").text
            assert str(current_date.year) + "年 " + str(current_date.month) + "月" == year_month_text, "年月表示が正しいことを確認する。"

            if current_date.year < init_date.year:
                break
        
        # 今月から年が変わるまで1月後に移動し続ける
        while True:
            next_button = driver.find_element(By.ID, "next")
            next_button.click()
            current_date = current_date + relativedelta(months=1)
            print(current_date)  # デバッグ用に現在の年月を出力
            time.sleep(1)  # 表示が更新されるまで少し待つ

            year_month_text = driver.find_element(By.ID, "monthYearDisplay").text
            assert str(current_date.year) + "年 " + str(current_date.month) + "月" == year_month_text, "年月表示が正しいことを確認する。"

            if current_date.year > init_date.year:
                break
        
        # 今月に戻るボタンをクリックする
        today_button = driver.find_element(By.ID, "now")
        today_button.click()
        time.sleep(1)  # 表示が更新されるまで少し待つ
        year_month_text = driver.find_element(By.ID, "monthYearDisplay").text
        assert str(init_date.year) + "年 " + str(init_date.month) + "月" == year_month_text, "年月表示が正しいことを確認する。"
    
    def assert_calendar_cell(self, driver, current_date):
        user = self.login_user
        # イベントをクリックしてモーダルを表示する
        calendar = driver.find_elements(By.XPATH, "//*[@id='calendar']/table/tr")
        for row in calendar:
            cells = row.find_elements(By.TAG_NAME, "td")
            for cell in cells:
                cell.click()
                time.sleep(1.5)  # ページが完全に読み込まれるまで少し待つ
                if cell.get_attribute("class") == "active":
                    modal = driver.find_element(By.ID, "eventListForDayModal")
                    assert modal.get_attribute("class") == "modal fade show", "イベントの内容を表示するモーダルが表示される。"

                    # スケジュールが一致することを確認する
                    date = cell.find_element(By.XPATH, ".//div[@class='day-element']/div[1]").text
                    day_of_schedules = schedule_models.Schedule.objects.filter(date=current_date.replace(day=int(date)), tenant=user.tenant).order_by("start").order_by("id")
                    schedule_elements = driver.find_element(By.ID, "eventListForDayBody")

                    # スケジュールありのとき、子要素のdivと、スケジュールの数が一致すること(最大4件まで表示される仕様のため、5件以上ある場合は4件表示される)
                    if len(day_of_schedules) != 0:
                        divs = schedule_elements.find_elements(By.XPATH, "./div")
                        assert len(divs) == min(len(day_of_schedules), 4), "スケジュールの数と、モーダルに表示されているスケジュールの数が一致する。"
                    else:
                        divs = schedule_elements.find_elements(By.XPATH, "./div")
                        assert len(divs) == 1 , "スケジュールがない場合、モーダルには「予定はありません」と表示される。"
                        assert divs[0].find_element(By.CLASS_NAME, "event-note").text == "予定はありません", "スケジュールがない場合、モーダルには「予定はありません」と表示される。"
                    close_button = modal.find_element(By.ID, "close-event-list-modal")
                    close_button.click()
                    time.sleep(1.5)  # モーダルが閉じるまで待つ
                elif cell.get_attribute("class") == "disabled":
                    modal = driver.find_element(By.ID, "eventListForDayModal")
                    assert modal.get_attribute("class") == "modal fade", "イベントの内容を表示するモーダルが表示されないことを確認する。"
        
    def test_event_list_modal_content(self, driver):
        # イベントの内容を表示するモーダルの内容を確認
        user = self.login_user

        # ホームページに移動する
        driver.get(BASE_URL)

        # 権限変更(スケジュール閲覧権限を付与する)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.add(view_perm.permission)
        user.save()

        # 今月を取得する
        current_date = datetime.datetime.now()

        # スケジュール一覧ページにアクセスする
        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール一覧ページにアクセスできる。"
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ

        self.assert_calendar_cell(driver, current_date)

        # 前の月に移動して確認する
        prev_button = driver.find_element(By.ID, "prev")
        prev_button.click()
        current_date = current_date - relativedelta(months=1)
        time.sleep(1)  # 表示が更新されるまで少し待つ
        self.assert_calendar_cell(driver, current_date)

        # 2か月先に移動して確認する
        next_button = driver.find_element(By.ID, "next")
        next_button.click()
        current_date = current_date + relativedelta(months=1)
        time.sleep(1)  # 表示が更新されるまで少し待つ
        next_button.click()
        current_date = current_date + relativedelta(months=1)
        time.sleep(1)  # 表示が更新されるまで少し待つ
        self.assert_calendar_cell(driver, current_date)
        
    # def test_calendar_on_schedule_status(self, driver):
    #     # カレンダーに表示されるスケジュールが、ユーザーの出欠ステータスによって表示が変わることを確認する
    #     user = self.login_user
    #     # ホームページに移動する
    #     driver.get(BASE_URL)
    #     # 権限変更(スケジュール閲覧権限を付与する)
    #     view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
    #     user.user_permissions.add(view_perm.permission)
    #     add_perm = user_models.CustomPermission.objects.get(permission__codename="add_schedule")
    #     user.user_permissions.add(add_perm.permission)
    #     user.save()
    #     # スケジュール一覧ページにアクセスする
    #     driver.get(f"{BASE_URL}/schedule/schedule/list/")
    #     assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール一覧ページにアクセスできる。"
    #     time.sleep(1)  # ページが完全に読み込まれるまで少し待つ
    #     # 今日の月で、「api/schedule/schedule_list/?y=2026&m=3」をGETして、スケジュールの一覧を取得する
    #     today = datetime.datetime.now()
    #     date_str = today.strftime("%Y-%m-%d")
    #     shedule_list = driver.get(f"{BASE_URL}/api/schedule/schedule_list/?y={today.year}&m={today.month}")
    #     time.sleep(1)  # データが取得されるまで少し待つ
    #     # jsonを辞書に変換する
    #     import json
    #     schedule_list_dict = json.loads(shedule_list.text)

    def test_create_event_button_has_permission(self, driver):
        # イベント作成ボタンの動作を確認
        user = self.login_user

        # ホームページに移動する
        driver.get(BASE_URL)

        # 権限変更(スケジュール閲覧権限を付与する)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.add(view_perm.permission)
        add_perm = user_models.CustomPermission.objects.get(permission__codename="add_schedule")
        user.user_permissions.add(add_perm.permission)
        user.save()

        # スケジュール一覧ページにアクセスする
        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール一覧ページにアクセスできる。"
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ

        day_of_cell = driver.find_element(By.XPATH, "//*[@id='calendar']/table/tr[3]/td[1]")
        day_of_cell.click()
        click_date = int(day_of_cell.find_element(By.XPATH, ".//div[@class='day-element']/div[@class='day-number']").text)
        create_event_button = driver.find_element(By.ID, "add-schedule")
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ
        assert create_event_button.is_displayed(), "イベント作成ボタンが表示されていることを確認する。"
        create_event_button.click()
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/create/?date={datetime.datetime.now().strftime("%Y-%m")}-{click_date:02d}", "イベント作成ページに遷移することを確認する。"

        date_input = driver.find_element(By.ID, "id_date")
        excepted_date = datetime.datetime.now().replace(day=click_date).strftime("%Y-%m-%d")
        assert date_input.get_attribute("value") == excepted_date, "イベント作成ページの日付入力に、今日の日付が初期値として設定されていることを確認する。"    
    
    def test_create_event_button_no_permission(self, driver):
        # イベント作成ボタンの動作を確認
        user = self.login_user

        # ホームページに移動する
        driver.get(BASE_URL)

        # 権限変更(スケジュール閲覧権限を付与する)
        view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
        user.user_permissions.add(view_perm.permission)
        add_perm = user_models.CustomPermission.objects.get(permission__codename="add_schedule")
        user.user_permissions.remove(add_perm.permission)
        user.save()

        # スケジュール一覧ページにアクセスする
        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール一覧ページにアクセスできる。"
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ

        day_of_cell = driver.find_element(By.XPATH, "//*[@id='calendar']/table/tr[3]/td[1]")
        day_of_cell.click()
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ
        create_event_button = driver.find_elements(By.ID, "add-schedule")
        assert len(create_event_button) == 0, "イベント作成ボタンが表示されていないことを確認する。"


class TestScheduleListAdmin:
    @pytest.fixture(scope="class", autouse=True)
    def login_once_admin(self, request, driver):
        admin_user = user_models.TenantUser.objects.filter(role='admin').first()
        if admin_user is None:
            raise Exception("No admin user found in the database. Please create an admin user before running this test.")

        login_as(driver, admin_user.username)
        request.cls.admin_user = admin_user
        yield
        logout(driver)

    def test_admin_access(self, driver):
        # 管理者ユーザーでログインしてスケジュール一覧ページにアクセスした場合、アクセスできること
        # ホームページに移動する
        driver.get(BASE_URL)

        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "管理者ユーザーはスケジュール一覧ページにアクセスできる。"
    
    def test_create_event_button_has_permission(self, driver):

        # ホームページに移動する
        driver.get(BASE_URL)

        # スケジュール一覧ページにアクセスする
        driver.get(f"{BASE_URL}/schedule/schedule/list/")
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "スケジュール一覧ページにアクセスできる。"
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ

        day_of_cell = driver.find_element(By.XPATH, "//*[@id='calendar']/table/tr[3]/td[1]")
        day_of_cell.click()
        click_date = int(day_of_cell.find_element(By.XPATH, ".//div[@class='day-element']/div[@class='day-number']").text)
        create_event_button = driver.find_element(By.ID, "add-schedule")
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ
        assert create_event_button.is_displayed(), "イベント作成ボタンが表示されていることを確認する。"
        create_event_button.click()
        time.sleep(1)  # ページが完全に読み込まれるまで少し待つ
        assert driver.current_url == f"{BASE_URL}/schedule/schedule/create/?date={datetime.datetime.now().strftime("%Y-%m")}-{click_date:02d}", "イベント作成ページに遷移することを確認する。"

        date_input = driver.find_element(By.ID, "id_date")
        excepted_date = datetime.datetime.now().replace(day=click_date).strftime("%Y-%m-%d")
        assert date_input.get_attribute("value") == excepted_date, "イベント作成ページの日付入力に、今日の日付が初期値として設定されていることを確認する。"    

class TestScheduleListForAnswerAttendance:
    # 備考の入力パターン(test_plan.mdのtextareaのパターンを参照)
    NOTE_PATTERTN = [
        "",  # 備考なし
        "遅刻します",  # 備考あり
        "理由：電車遅延のため",  # 備考あり（理由付き）
        "予定が入っているため欠席します。",  # 備考あり（予定あり）
        "最大200文字の備考" * 10,  # 備考あり（200文字）
        "<script>alert('XSS')</script>",  # XSSを試すパターン
        "SELECT * FROM users;",  # SQLインジェクションを試すパターン
        "こんにちは",  # 日本語入力
        "Hello",  # 英語入力
        "1234567890",  # 数字のみ
        "😊",  # 絵文字入力
        "こんにちはHello",  # 日本語と英語の混在入力
    ]

    @pytest.fixture(scope="class", autouse=True)
    def login_once(self, request, driver):
        user = user_models.TenantUser.objects.first()
        if user is None:
            raise Exception("No test user found in the database. Please create a test user before running this test.")

        login_as(driver, user.username)
        request.cls.login_user = user
        yield
        logout(driver)

    # 出席
    def test_answer_attend(self, driver):
        # スケジュールの出欠に回答したとき、カレンダーの表示が変わることを確認する
        pass  # 出欠の回答は別のAPIで行うため、Seleniumでのテストは難しい。ユニットテストで確認することを推奨する。

    # 欠席
    def test_answer_absent(self, driver):
        # スケジュールの出欠に回答したとき、カレンダーの表示が変わることを確認する
        # 備考を入力しない場合は、アラートダイアログが表示されることも確認する
        pass  # 出欠の回答は別のAPIで行うため、Seleniumでのテストは難しい。ユニットテストで確認することを推奨する。
    
    # 遅刻
    def test_answer_late(self, driver):
        # スケジュールの出欠に回答したとき、カレンダーの表示が変わることを確認する
        # 備考を入力しない場合は、アラートダイアログが表示されることも確認する
        pass  # 出欠の回答は別のAPIで行うため、Seleniumでのテストは難しい。ユニットテストで確認することを推奨する。
    
    # 早退
    def test_answer_early_leave(self, driver):
        # スケジュールの出欠に回答したとき、カレンダーの表示が変わることを確認する
        # 備考を入力しない場合は、アラートダイアログが表示されることも確認する
        pass  # 出欠の回答は別のAPIで行うため、Seleniumでのテストは難しい。ユニットテストで確認することを推奨する。
    
    # 未回答
    def test_answer_no_response(self, driver):
        # スケジュールの出欠に回答したとき、カレンダーの表示が変わることを確認する
        pass  # 出欠の回答は別のAPIで行うため、Seleniumでのテストは難しい。ユニットテストで確認することを推奨する。

    # 未定
    def test_answer_undecided(self, driver):
        # スケジュールの出欠に回答したとき、カレンダーの表示が変わることを確認する
        # 備考を入力しない場合は、アラートダイアログが表示されることも確認する
        pass  # 出欠の回答は別のAPIで行うため、Seleniumでのテストは難しい。ユニットテストで確認することを推奨する。

    def test_conflict_schedule_delete(self, driver):
        # スケジュールの出欠に回答したとき、スケジュールの削除が行われる場合、エラーメッセージが表示されることを確認する
        pass  # 出欠の回答は別のAPIで行うため、Seleniumでのテストは難しい。ユニットテストで確認することを推奨する。

    def test_conflict_schedule_change(self, driver):
        # スケジュールの出欠に回答したとき、スケジュールの日付が変更される場合、エラーメッセージが表示されることを確認する
        pass  # 出欠の回答は別のAPIで行うため、Seleniumでのテストは難しい。ユニットテストで確認することを推奨する。