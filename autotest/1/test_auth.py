from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os
import logging
from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, filename="tax_audit_scraper.log", format="%(asctime)s - %(levelname)s - %(message)s")

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
BASE_URL = "https://id.adata.kz/"  # URL сайта
OUTPUT_CSV = "auth_results.csv"
OUTPUT_TXT = "auth_results.txt"
SCREENSHOT_DIR = "screenshots"

def init_driver():
    """Initialize Chrome WebDriver with options."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def wait_for_element(driver, by, value, timeout=20):
    """Wait for element to be present."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def save_screenshot(driver, test_name, filename):
    """Save screenshot for a specific test."""
    test_dir = os.path.join(SCREENSHOT_DIR, test_name)
    os.makedirs(test_dir, exist_ok=True)
    screenshot_path = os.path.join(test_dir, filename)
    driver.save_screenshot(screenshot_path)
    logging.info(f"Saved screenshot for test {test_name}: {screenshot_path}")

def write_result(test_name, result):
    """Write test result to CSV and TXT."""
    file_exists = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Тест", "Результат"])
        writer.writerow([test_name, result])
    
    with open(OUTPUT_TXT, "a", encoding='utf-8') as f:
        f.write(f"Тест: {test_name}, Результат: {result}\n")
    
    logging.info(f"Wrote result for test {test_name}: {result}")

def login(driver):
    """Perform login action."""
    try:
        driver.get(BASE_URL)
        wait_for_element(driver, By.XPATH, "//div[contains(., 'Вход') and contains(@class, 'cursor-pointer')]").click()
        
        email_field = wait_for_element(driver, By.ID, "Введите email")
        password_field = wait_for_element(driver, By.ID, "Введите пароль")
        login_button = wait_for_element(driver, By.XPATH, "//button[span[text()='Продолжить']]")
        
        email_field.send_keys(LOGIN)
        password_field.send_keys(PASSWORD)
        login_button.click()
        
        WebDriverWait(driver, 20).until(EC.url_contains("/dashboard"))
        logging.info("Successfully logged in")
        print("🟢 Авторизация успешна")
        return True
    except Exception as e:
        logging.error(f"Login error: {e}")
        print(f"❌ Ошибка при авторизации: {e}")
        save_screenshot(driver, "login", f"error_login_{int(time.time())}.png")
        return False

def test_user_registration(driver):
    """Test user registration."""
    try:
        driver.get(BASE_URL + "register")  # Замените на реальный путь
        email_field = wait_for_element(driver, By.ID, "Введите email")  # Замените на реальный ID
        password_field = wait_for_element(driver, By.ID, "Введите пароль")  # Замените на реальный ID
        confirm_password_field = wait_for_element(driver, By.ID, "confirm_password")  # Замените на реальный ID
        submit_button = wait_for_element(driver, By.XPATH, "//button[span[text()='Продолжить']]")
        
        email_field.send_keys("newuser@adata.kz")
        password_field.send_keys(PASSWORD)
        confirm_password_field.send_keys(PASSWORD)
        submit_button.click()
        
        success_message = wait_for_element(driver, By.CLASS_NAME, "success-message")  # Замените на реальный селектор
        if "Registration successful" in success_message.text:
            logging.info("Registration test passed")
            print("🟢 Регистрация успешна")
            return "Успех"
        else:
            logging.warning("Registration test failed: unexpected success message")
            print("⚠️ Неожиданное сообщение об успехе")
            return "Неожиданное сообщение"
    except Exception as e:
        logging.error(f"Registration test error: {e}")
        print(f"❌ Ошибка при регистрации: {e}")
        save_screenshot(driver, "registration", f"error_registration_{int(time.time())}.png")
        return f"Ошибка: {str(e)}"

def test_remember_me(driver):
    """Test 'Remember me' checkbox."""
    try:
        driver.get(BASE_URL + "login")
        wait_for_element(driver, By.XPATH, "//div[contains(., 'Вход') and contains(@class, 'cursor-pointer')]").click()
        
        remember_me = wait_for_element(driver, By.ID, "check")
        
        # Check if checkbox is selected by default
        if not remember_me.is_selected():
            remember_me.click()
        assert remember_me.is_selected(), "Чекбокс 'Запомнить меня' не включен"
        
        # Uncheck and verify
        remember_me.click()
        assert not remember_me.is_selected(), "Чекбокс 'Запомнить меня' не выключен"
        
        # Check again
        remember_me.click()
        assert remember_me.is_selected(), "Чекбокс 'Запомнить меня' не включен повторно"
        
        logging.info("Remember me test passed")
        print("🟢 Тест 'Запомнить меня' успешен")
        return "Успех"
    except Exception as e:
        logging.error(f"Remember me test error: {e}")
        print(f"❌ Ошибка при тестировании 'Запомнить меня': {e}")
        save_screenshot(driver, "remember_me", f"error_remember_me_{int(time.time())}.png")
        return f"Ошибка: {str(e)}"

def test_forgot_password_button(driver):
    """Test 'Forgot password?' button."""
    try:
        driver.get(BASE_URL + "login")
        wait_for_element(driver, By.XPATH, "//div[contains(., 'Вход') and contains(@class, 'cursor-pointer')]").click()
        
        forgot_password = wait_for_element(driver, By.ID, "forgot_password")  # Замените на реальный ID
        forgot_password.click()
        
        modal = wait_for_element(driver, By.ID, "password_reset_modal")  # Замените на реальный ID
        assert modal.is_displayed(), "Модальное окно восстановления пароля не отображается"
        
        logging.info("Forgot password button test passed")
        print("🟢 Тест кнопки 'Забыли пароль?' успешен")
        return "Успех"
    except Exception as e:
        logging.error(f"Forgot password button test error: {e}")
        print(f"❌ Ошибка при тестировании кнопки 'Забыли пароль?': {e}")
        save_screenshot(driver, "forgot_password", f"error_forgot_password_{int(time.time())}.png")
        return f"Ошибка: {str(e)}"

def test_password_reset(driver):
    """Test password reset functionality."""
    try:
        driver.get(BASE_URL + "forgot-password")  # Замените на реальный путь
        email_field = wait_for_element(driver, By.ID, "reset_email")  # Замените на реальный ID
        submit_button = wait_for_element(driver, By.XPATH, "//button[span[text()='Продолжить']]")
        
        email_field.send_keys("testuser@adata.kz")
        assert email_field.get_attribute("value") == "testuser@adata.kz", "Маска email не работает"
        
        submit_button.click()
        
        notification = wait_for_element(driver, By.CLASS_NAME, "notification")  # Замените на реальный селектор
        assert "На вашу почту мы вышлем инструкции по сбросу пароля" in notification.text, "Уведомление не отображается"
        
        logging.info("Password reset test passed")
        print("🟢 Тест восстановления пароля успешен")
        return "Успех"
    except Exception as e:
        logging.error(f"Password reset test error: {e}")
        print(f"❌ Ошибка при тестировании восстановления пароля: {e}")
        save_screenshot(driver, "password_reset", f"error_password_reset_{int(time.time())}.png")
        return f"Ошибка: {str(e)}"

def main():
    """Run all authentication tests."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    driver = init_driver()
    try:
        # Test registration
        print("\n🔎 Тестирование регистрации")
        result = test_user_registration(driver)
        write_result("Регистрация", result)
        
        # Test login
        print("\n🔎 Тестирование авторизации")
        result = login(driver)
        write_result("Авторизация", "Успех" if result else "Ошибка")
        
        # Test remember me
        print("\n🔎 Тестирование чекбокса 'Запомнить меня'")
        result = test_remember_me(driver)
        write_result("Запомнить меня", result)
        
        # Test forgot password button
        print("\n🔎 Тестирование кнопки 'Забыли пароль?'")
        result = test_forgot_password_button(driver)
        write_result("Кнопка 'Забыли пароль?'", result)
        
        # Test password reset
        print("\n🔎 Тестирование восстановления пароля")
        result = test_password_reset(driver)
        write_result("Восстановление пароля", result)
        
    finally:
        driver.quit()
        print("✅ Тестирование завершено")
        logging.info("All tests completed")

if __name__ == "__main__":
    main()