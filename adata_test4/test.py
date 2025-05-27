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

# Configure logging
logging.basicConfig(level=logging.INFO, filename="tax_audit_scraper.log", format="%(asctime)s - %(levelname)s - %(message)s")

LOGIN = ""
PASSWORD = ""
BIN_FILE = "bin_list.txt"
OUTPUT_CSV = "tax_audit_results.csv"
OUTPUT_TXT = "tax_audit_results.txt"
SCREENSHOT_DIR = "screenshots"

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def wait_for_element(driver, by, value, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def login(driver):
    driver.get("https://pk.adata.kz/")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'Вход') and contains(@class, 'cursor-pointer')]"))).click()

    try:
        wait_for_element(driver, By.ID, "Введите email").send_keys(LOGIN)
        wait_for_element(driver, By.ID, "Введите пароль").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[contains(., 'Войти')]").click()
        logging.info("Successfully logged in")
    except Exception as e:
        logging.error(f"Login error: {e}")
        print(f"❌ Ошибка при вводе данных авторизации: {e}")
        raise

def search_company(driver, bin_value):
    try:
        search_input = wait_for_element(driver, By.XPATH, "//input[@type='search']")
        search_input.clear()
        search_input.send_keys(bin_value)
        wait_for_element(driver, By.XPATH, "//button[contains(., 'Найти')]").click()
        time.sleep(2)
        logging.info(f"Successfully searched for BIN: {bin_value}")
        return True
    except Exception as e:
        logging.error(f"Search error for BIN {bin_value}: {e}")
        print(f"❌ Ошибка поиска БИН {bin_value}: {e}")
        return False

def open_company_profile(driver):
    try:
        wait_for_element(driver, By.XPATH, "//a[contains(@href, '/company/')]").click()
        logging.info("Opened company profile")
        return True
    except Exception as e:
        logging.error(f"Error opening company profile: {e}")
        print(f"⚠️ Не удалось открыть профиль: {e}")
        return False

def go_to_reliability_tab(driver, bin_value):
    try:
        wait = WebDriverWait(driver, 20)

        # Click "Благонадежность" tab
        reliability_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Благонадежность']/..")))
        reliability_tab.click()
        print("🟢 Вкладка 'Благонадежность' открыта")
        logging.info("Opened 'Благонадежность' tab")
        time.sleep(2)

        # Click "Предприятие" button
        enterprise_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Предприятие']]")))
        enterprise_button.click()
        print("🟢 Подраздел 'Предприятие' открыт")
        logging.info("Opened 'Предприятие' section")
        time.sleep(2)

        # Check if "Выбрать" button exists
        choose_button_xpath = "//span[text()='Выбрать']/.."
        choose_buttons = driver.find_elements(By.XPATH, choose_button_xpath)
        if choose_buttons:
            choose_button = wait.until(EC.element_to_be_clickable((By.XPATH, choose_button_xpath)))
            choose_button.click()
            print("🟢 Кнопка 'Выбрать' нажата")
            logging.info("Clicked 'Выбрать' button")
            time.sleep(2)
        else:
            print("⚠️ Кнопка 'Выбрать' не найдена, продолжаем без нажатия")
            logging.warning(f"'Выбрать' button not found for BIN {bin_value}, proceeding without clicking")
            save_screenshot(driver, bin_value, f"debug_no_choose_button_{bin_value}.png")

        return True
    except Exception as e:
        logging.error(f"Error in go_to_reliability_tab for BIN {bin_value}: {e}")
        print(f"❌ Ошибка при открытии 'Благонадежность → Предприятие → Выбрать': {e}")
        save_screenshot(driver, bin_value, f"debug_reliability_tab_{bin_value}.png")
        return False

def check_tax_status(driver, bin_value):
    try:
        label = "В списке «Профилактический контроль и надзор на 1-ое полугодие 2025 года"
        xpath = f"//div[contains(@class, 'text-deepblue-900') and contains(.//span, '{label}')]//div[contains(@class, 'flex w-full items-start md:w-fit')]"
        status_element = wait_for_element(driver, By.XPATH, xpath)
        status_text = status_element.text.strip()
        print(f"📌 Найден статус: {status_text}")
        logging.info(f"Tax audit status for BIN {bin_value}: {status_text}")
        return status_text if status_text in ["Да", "Нет"] else "Не найдено"
    except Exception as e:
        logging.error(f"Error checking tax audit status for BIN {bin_value}: {e}")
        print(f"❌ Ошибка при проверке статуса: {e}")
        save_screenshot(driver, bin_value, f"debug_tax_status_{bin_value}.png")
        return "Ошибка"

def write_result(bin_value, result):
    # Write to CSV
    file_exists = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["БИН", "Статус"])
        writer.writerow([bin_value, result])
    
    # Write to TXT
    with open(OUTPUT_TXT, "a", encoding='utf-8') as f:
        f.write(f"БИН: {bin_value}, Статус: {result}\n")
    
    logging.info(f"Wrote result for BIN {bin_value}: {result} to CSV and TXT")

def save_screenshot(driver, bin_value, filename):
    # Create directory for the BIN if it doesn't exist
    bin_dir = os.path.join(SCREENSHOT_DIR, bin_value)
    os.makedirs(bin_dir, exist_ok=True)
    
    # Save screenshot in the BIN-specific directory
    screenshot_path = os.path.join(bin_dir, filename)
    driver.save_screenshot(screenshot_path)
    logging.info(f"Saved screenshot for BIN {bin_value}: {screenshot_path}")

def main():
    # Create screenshots directory
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with open(BIN_FILE, "r") as f:
        bin_list = [line.strip() for line in f if line.strip()]

    driver = init_driver()
    try:
        login(driver)
        for bin_value in bin_list:
            print(f"\n🔎 Проверка БИН: {bin_value}")
            logging.info(f"Processing BIN: {bin_value}")
            try:
                if not search_company(driver, bin_value):
                    write_result(bin_value, "Ошибка поиска")
                    continue
                if not open_company_profile(driver):
                    write_result(bin_value, "Ошибка открытия профиля")
                    continue
                if not go_to_reliability_tab(driver, bin_value):
                    write_result(bin_value, "Ошибка открытия вкладки")
                    continue
                result = check_tax_status(driver, bin_value)
                print(f"📌 Статус: {result}")
                write_result(bin_value, result)
                save_screenshot(driver, bin_value, f"screenshot_{bin_value}.png")
            except Exception as e:
                logging.error(f"General error for BIN {bin_value}: {e}")
                print(f"❗ Ошибка с БИН {bin_value}: {e}")
                save_screenshot(driver, bin_value, f"screenshot_{bin_value}.png")
            finally:
                driver.get("https://pk.adata.kz/")
                time.sleep(3)
    finally:
        driver.quit()
        print("✅ Завершено.")
        logging.info("Script completed")

if __name__ == "__main__":
    main()
