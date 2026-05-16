import os
import sys

import django
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import time


BASE_URL = "http://localhost:8000"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orchestra_rls.settings")
django.setup()


@pytest.fixture(scope="session")
def driver():
	driver_path = os.path.join(os.path.dirname(__file__), "msedgedriver.exe")
	service = Service(executable_path=driver_path)
	edge_driver = webdriver.Edge(service=service)
	yield edge_driver
	edge_driver.quit()


@pytest.fixture(autouse=True)
def reset_browser_state(driver):
	# セッション共有ドライバーでもテスト間の状態を分離する。
	driver.get(BASE_URL)
	driver.delete_all_cookies()
	driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
	yield
	driver.get(BASE_URL)
	driver.delete_all_cookies()
	driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")


def login_as(driver, username, password="dspfpasswd0", wait_seconds=2):
	driver.get(f"{BASE_URL}/user/login/")
	email_input = driver.find_element(By.NAME, "username")
	password_input = driver.find_element(By.NAME, "password")
	email_input.send_keys(username)
	password_input.send_keys(password)
	driver.find_element(By.ID, "btn-login").click()
	if wait_seconds > 0:
		time.sleep(wait_seconds)


def logout(driver, wait_seconds=1):
	driver.find_element(By.ID, "btn-menu").click()
	if wait_seconds > 0:
		time.sleep(wait_seconds)
	driver.find_element(By.ID, "btn-logout").click()
