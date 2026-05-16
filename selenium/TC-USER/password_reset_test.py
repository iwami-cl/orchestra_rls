import uuid
import time
from selenium.webdriver.common.by import By
from user import models as user_models

BASE_URL = "http://localhost:8000"


class TestPasswordReset:
	# 実行コマンド: pytest -v selenium/TC-USER/password_reset_test.py
	def test_no_login_access(self, driver):
		# 未ログイン状態でパスワードリセットページにアクセスできること（ログインページにリダイレクトされないこと）
		test_user = user_models.TenantUser.objects.first()
		urls = [
			f"{BASE_URL}/user/password_reset?user_id={test_user.user_id}",  # 未ログインだがuser_idがある場合（不正なアクセス user_idなしのURLにリダイレクトされることを確認）
			f"{BASE_URL}/user/password_reset",  # 未ログインでuser_idがない場合（正しいアクセス）
		]
		for url in urls:
			driver.get(url)
			# 入力欄の確認(未ログイン時は、new_password1,new_password2,emailが画面上にある)
			password_input = driver.find_elements(By.NAME, "new_password1")
			email_input = driver.find_elements(By.NAME, "email")
			assert len(password_input) == 1, "Password reset form was not rendered for unauthenticated user."
			assert len(email_input) == 1, "Email input should be present for unauthenticated user."
			password_confirm_input = driver.find_elements(By.NAME, "new_password2")
			assert len(password_confirm_input) == 1, "Password confirmation field should be present for unauthenticated user."

	def test_login_access(self, driver):
		# ログイン状態でパスワードリセットページにアクセスした場合、ログインユーザーのuser_idを含むURLにリダイレクトされること
		test_user = user_models.TenantUser.objects.first()

		# まずログインする
		driver.get(f"{BASE_URL}/user/login/")
		username_input = driver.find_element(By.NAME, "username")
		password_input = driver.find_element(By.NAME, "password")
		username_input.send_keys(test_user.username)
		password_input.send_keys("dspfpasswd0")  # Replace with the actual password for the test user
		
		login_btn = driver.find_element(By.ID, "btn-login")
		login_btn.click()
		
		driver.get(f"{BASE_URL}/user/password_reset?user_id={str(test_user.user_id)}")  # user_idがある場合（正しいアクセス）
		assert driver.current_url == f"{BASE_URL}/user/password_reset?user_id={str(test_user.user_id)}", "Authenticated user should be redirected to password reset page with their user_id in the URL."

		# 入力欄の確認
		password_input = driver.find_elements(By.NAME, "new_password1")
		email_input = driver.find_elements(By.NAME, "email")
		assert len(password_input) == 1, "Password reset form was not rendered for authenticated user."
		assert len(email_input) == 0, "Email input should not be present for authenticated user."
		password_confirm_input = driver.find_elements(By.NAME, "new_password2")
		assert len(password_confirm_input) == 1, "Password confirmation field should be present for authenticated user."

		
		driver.get(f"{BASE_URL}/user/password_reset")  # user_idがない場合（不正アクセス ユーザー一覧または、ホーム画面にリダイレクトされることを確認）
		assert driver.current_url in [f"{BASE_URL}/user/user_list/", f"{BASE_URL}/"], "Authenticated user should be redirected to tenant user list or home page when accessing password reset without user_id."

		# ログアウトする
		driver.find_element(By.ID, "btn-menu").click()
		# 1秒待つ
		time.sleep(1)
		driver.find_element(By.ID, "btn-logout").click()