import os
import sys
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.config.config import Base_URL, new_username, profile_url, email, pwd
from src.locators.locators import *

# ==================== WebDriver Setup ====================
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # use classic headless for CI stability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

# ==================== Test Logic ====================
def login_naukri(driver, username, password):
    driver.get(Base_URL)

    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
        )
        login_btn.click()
    except TimeoutException:
        driver.save_screenshot("login_button_missing.png")
        pytest.fail("Login button not found on the page.")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, user_xpath)))
        email_input = driver.find_element(By.XPATH, user_xpath)
        email_input.send_keys(username)

        password_input = driver.find_element(By.XPATH, pwd_xpath)
        password_input.send_keys(password)

        submit_btn = driver.find_element(By.XPATH, login_button_xpath)
        submit_btn.click()
    except Exception as e:
        driver.save_screenshot("login_form_failed.png")
        pytest.fail(f"Login form interaction failed: {e}")

    # Wait for profile to load
    driver.get(profile_url)
    try:
        edit_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, user_name_edit_icon_xpath))
        )
        edit_icon.click()
    except TimeoutException:
        driver.save_screenshot("edit_icon_not_found.png")
        pytest.fail("Profile edit icon not found.")

    try:
        first_name_input = driver.find_element(By.XPATH, first_name_input_xpath)
        first_name_input.clear()
        first_name_input.send_keys(new_username)

        save_button = driver.find_element(By.XPATH, save_button_xpath)
        save_button.click()
    except Exception as e:
        driver.save_screenshot("name_update_failed.png")
        pytest.fail(f"Name update failed: {e}")

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    return "My Naukri" in driver.page_source

# ==================== Test ====================
def test_login_naukri(driver):
    USERNAME = email
    PASSWORD = pwd
    try:
        assert login_naukri(driver, USERNAME, PASSWORD), "Login or profile update failed."
    finally:
        driver.save_screenshot("final_state.png")
