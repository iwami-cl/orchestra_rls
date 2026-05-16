from conftest import BASE_URL, driver, login_as, logout
from selenium.webdriver.common.by import By
import schedule
from user import models as user_models
from schedule import models as schedule_models
import datetime
import pytest
import time


# 実行コマンド: pytest -v selenium/TC-SCHEDULE/04_schedule_delete_test.py
@pytest.fixture(autouse=True)
def reset_browser_state(driver):
	# このファイルではクラス単位でログイン状態を維持するため、クッキーは消さずに画面遷移のみ行う。
	driver.get(BASE_URL)
	yield
	driver.get(BASE_URL)

@pytest.fixture
def create_schedule_for_test(request):
	tenant = None
	if hasattr(request, "cls") and hasattr(request.cls, "login_user"):
		tenant = request.cls.login_user.tenant
	elif hasattr(request, "cls") and hasattr(request.cls, "admin_user"):
		tenant = request.cls.admin_user.tenant
	else:
		user = user_models.TenantUser.objects.first()
		if user is None:
			raise Exception("No test user found in the database. Please create a test user before running this test.")
		tenant = user.tenant

	schedule = schedule_models.Schedule.objects.create(
		date=datetime.date.today(),
		start=datetime.time(10, 0),
		end=datetime.time(12, 0),
		title="Selenium削除テスト用スケジュール",
		place="テスト会場",
		tenant=tenant,
	)
	yield schedule
	for s in schedule_models.Schedule.objects.filter(id=schedule.id):
		s.delete()


class TestDeleteScheduleNoLogin:
	def test_no_login_access(self, driver, create_schedule_for_test):
		# 未ログイン状態を明示的に作る
		driver.get(BASE_URL)
		driver.delete_all_cookies()

		schedule = create_schedule_for_test

		driver.get(f"{BASE_URL}/schedule/schedule/delete/{schedule.id}")
		assert driver.current_url.startswith(f"{BASE_URL}/user/login/"), "未ログインユーザーはスケジュール削除ページにアクセスできず、ログインページにリダイレクトされる必要があります。"


class TestDeleteSchedule:
	@pytest.fixture(scope="class", autouse=True)
	def login_once(self, request, driver):
		user = user_models.TenantUser.objects.first()
		if user is None:
			raise Exception("No test user found in the database. Please create a test user before running this test.")

		login_as(driver, user.username)
		request.cls.login_user = user
		yield
		logout(driver)

	def test_delete_schedule_form(self, driver, create_schedule_for_test):
		user = self.login_user
		schedule = create_schedule_for_test

		# 権限付与
		perm = user_models.CustomPermission.objects.get(permission__codename="delete_schedule")
		user.user_permissions.add(perm.permission)
		user.save()

		# ホームページに移動する
		driver.get(BASE_URL)

		# スケジュール削除ページにアクセスする
		driver.get(f"{BASE_URL}/schedule/schedule/delete/{schedule.id}")
		assert driver.current_url == f"{BASE_URL}/schedule/schedule/delete/{schedule.id}", "スケジュール削除ページにアクセスできる必要があります。"

		# 確認文言とボタンの確認
		header = driver.find_elements(By.ID, "header")
		assert len(header) == 1, "削除確認ヘッダーが表示される必要があります。"
		assert "削除しますか？" in header[0].text, "削除確認ヘッダーに正しい文言が表示される必要があります。"

		submit_btn = driver.find_elements(By.ID, "btn-delete")
		assert len(submit_btn) == 1, "削除実行ボタンが表示される必要があります。"

	def test_delete_schedule_execute(self, driver, create_schedule_for_test):
		user = self.login_user
		schedule = create_schedule_for_test

		# 権限付与
		delete_perm = user_models.CustomPermission.objects.get(permission__codename="delete_schedule")
		view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
		user.user_permissions.add(delete_perm.permission)
		user.user_permissions.add(view_perm.permission)
		user.save()

		# ホームページに移動する
		driver.get(BASE_URL)

		# 削除を実行する
		driver.get(f"{BASE_URL}/schedule/schedule/delete/{schedule.id}")
		driver.find_element(By.ID, "btn-delete").click()
		time.sleep(1)  # 削除処理が完了するまで少し待つ

		assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "削除後はスケジュール一覧ページに遷移する必要があります。"
		assert not schedule_models.Schedule.objects.filter(id=schedule.id).exists(), "削除実行後は対象スケジュールが削除されている必要があります。"

	def test_no_permission_access(self, driver, create_schedule_for_test):
		# 権限のないユーザーでログインしてスケジュール削除ページにアクセスした場合、アクセスできないこと
		user = self.login_user
		schedule = create_schedule_for_test

		# 権限変更(スケジュール削除権限を剥奪して、スケジュール閲覧権限を付与する)
		delete_perm = user_models.CustomPermission.objects.get(permission__codename="delete_schedule")
		user.user_permissions.remove(delete_perm.permission)
		view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
		user.user_permissions.add(view_perm.permission)
		user.save()

		# ホームページに移動する
		driver.get(BASE_URL)

		driver.get(f"{BASE_URL}/schedule/schedule/delete/{schedule.id}")
		assert driver.current_url == f"{BASE_URL}/schedule/schedule/list/", "権限のないユーザーはスケジュール削除ページにアクセスできず、スケジュール一覧ページにリダイレクトされる必要があります。"

		# 権限変更(スケジュール閲覧権限を剥奪する)
		user.user_permissions.remove(view_perm.permission)
		user.save()

		driver.get(f"{BASE_URL}/schedule/schedule/delete/{schedule.id}")
		assert driver.current_url.startswith(f"{BASE_URL}/"), "スケジュール閲覧権限のないユーザーはスケジュール削除ページにアクセスできず、ホームページにリダイレクトされる必要があります。"

	def test_has_permission_access(self, driver, create_schedule_for_test):
		# 権限のあるユーザーでログインしてスケジュール削除ページにアクセスした場合、アクセスできること
		user = self.login_user
		schedule = create_schedule_for_test

		# 権限変更(スケジュール削除権限を付与する)
		delete_perm = user_models.CustomPermission.objects.get(permission__codename="delete_schedule")
		user.user_permissions.add(delete_perm.permission)
		user.save()

		# ホームページに移動する
		driver.get(BASE_URL)

		driver.get(f"{BASE_URL}/schedule/schedule/delete/{schedule.id}")
		assert driver.current_url == f"{BASE_URL}/schedule/schedule/delete/{schedule.id}", "権限のあるユーザーはスケジュール削除ページにアクセスできる必要があります。"
		
	def test_cancel_button(self, driver, create_schedule_for_test):
		# スケジュール削除ページのキャンセルボタンがスケジュール詳細ページに遷移すること
		user = self.login_user
		schedule = create_schedule_for_test
		# 権限変更(スケジュール削除権限を付与する)
		delete_perm = user_models.CustomPermission.objects.get(permission__codename="delete_schedule")
		view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
		user.user_permissions.add(delete_perm.permission)
		user.user_permissions.add(view_perm.permission)
		user.save()
		# ホームページに移動する
		driver.get(BASE_URL)
		driver.get(f"{BASE_URL}/schedule/schedule/delete/{schedule.id}")
		driver.find_element(By.ID, "btn-cancel").click()
		assert driver.current_url == f"{BASE_URL}/schedule/schedule/detail/{schedule.id}", "キャンセルボタンをクリックした場合、スケジュール詳細ページに遷移する必要があります。"
		
	def test_delete_conflict(self, driver, create_schedule_for_test):
		# スケジュール削除の競合テスト（削除対象のスケジュールが既に削除されている場合、エラーメッセージが表示されること）
		user = self.login_user
		schedule = create_schedule_for_test

		# 権限変更(スケジュール削除権限を付与する)
		delete_perm = user_models.CustomPermission.objects.get(permission__codename="delete_schedule")
		view_perm = user_models.CustomPermission.objects.get(permission__codename="view_schedule")
		user.user_permissions.add(delete_perm.permission)
		user.user_permissions.add(view_perm.permission)

		user.save()

		# ホームページに移動する
		driver.get(BASE_URL)

		# 先にスケジュールを削除しておく
		target_id = schedule.id
		schedule.delete()

		# 削除を実行する
		driver.get(f"{BASE_URL}/schedule/schedule/delete/{target_id}")
		error_message = driver.find_elements(By.CLASS_NAME, "alert-error")
		assert len(error_message) == 1, "スケジュール削除の競合が発生した場合、エラーメッセージが表示される必要があります。"


class TestDeleteScheduleAdmin:
	@pytest.fixture(scope="class", autouse=True)
	def login_once_admin(self, request, driver):
		admin_user = user_models.TenantUser.objects.filter(role="admin").first()
		if admin_user is None:
			raise Exception("No admin user found in the database. Please create an admin user before running this test.")

		login_as(driver, admin_user.username)
		request.cls.admin_user = admin_user
		yield
		logout(driver)

	def test_admin_access(self, driver, create_schedule_for_test):
		# adminユーザーでログインしてスケジュール削除ページにアクセスした場合、アクセスできること
		schedule = create_schedule_for_test

		# ホームページに移動する
		driver.get(BASE_URL)

		driver.get(f"{BASE_URL}/schedule/schedule/delete/{schedule.id}")
		assert driver.current_url == f"{BASE_URL}/schedule/schedule/delete/{schedule.id}", "adminユーザーはスケジュール削除ページにアクセスできる必要があります。"
