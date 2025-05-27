from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Замените на свои данные
LOGIN = ""
PASSWORD = ""

# Файл со списком БИНов
BIN_FILE = "bin_list.txt"

# Инициализация Chrome WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")  # Можно включить для запуска без UI
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Авторизация на сайте ADATA
def login(driver):
    driver.get("https://pk.adata.kz/")
    time.sleep(5)

    # Нажать кнопку "Вход"
    try:
        login_button = driver.find_element(By.XPATH, "//div[contains(@class, 'cursor-pointer') and contains(., 'Вход')]")
        login_button.click()
        print("🟢 Кнопка 'Вход' нажата.")
    except Exception as e:
        print("❌ Не удалось нажать кнопку входа:", e)
        return

    time.sleep(5)

    # Ввод email и пароля на id.adata.kz
    try:
        email_input = driver.find_element(By.XPATH, "//input[@type='email' and @id='Введите email']")
        password_input = driver.find_element(By.XPATH, "//input[@type='password' and @id='Введите пароль']")

        email_input.clear()
        email_input.send_keys(LOGIN)
        password_input.clear()
        password_input.send_keys(PASSWORD)

        submit_button = driver.find_element(By.XPATH, "//button[contains(., 'Войти')]")
        submit_button.click()

        print("✅ Авторизация выполнена.")
    except Exception as e:
        print("❌ Ошибка при вводе данных авторизации:", e)

    time.sleep(5)

# 🔍 Поиск компании по БИН
def search_company(driver, bin_value):
    try:
        # Поиск поля с id (поиск по placeholder/id совпадает)
        search_input = driver.find_element(By.XPATH, "//input[@type='search' and @id='Введите ИИН, БИН, ФИО, название компании']")
        search_input.clear()
        search_input.send_keys(bin_value)
        time.sleep(1)

        # Кликаем по кнопке "Найти"
        search_button = driver.find_element(By.XPATH, "//button[contains(., 'Найти')]")
        search_button.click()
        print(f"🔎 Поиск выполнен для БИН: {bin_value}")
        time.sleep(3)
    except Exception as e:
        print(f"❌ Ошибка поиска по БИН {bin_value}: {e}")


# 📄 Открыть профиль компании
def open_company_profile(driver):
    try:
        # Ждём появления результатов
        time.sleep(2)
        # Первый результат в списке — ссылка на компанию
        first_result = driver.find_element(By.XPATH, "//a[contains(@href, '/company/')]")
        first_result.click()
        print("🟢 Переход к карточке компании.")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"⚠️ Не удалось открыть профиль компании: {e}")
        return False


# 🧾 Перейти в раздел "Благонадежность → Предприятие"
def go_to_reliability_tab(driver):
    try:
        driver.find_element(By.XPATH, "//a[contains(text(), 'Благонадежность')]").click()
        time.sleep(2)
        driver.find_element(By.XPATH, "//a[contains(text(), 'Предприятие')]").click()
        time.sleep(2)
    except:
        print("⚠️ Раздел 'Благонадежность' не найден")

# 📌 Проверить значение по выездным проверкам
def check_customs_status(driver):
    try:
        label = "Комплексные выездные таможенные проверки на 1-ое полугодие 2025 года"
        xpath = f"//*[contains(text(), '{label}')]/following-sibling::*"
        status = driver.find_element(By.XPATH, xpath).text.strip()
        return status
    except:
        return "Не найдено"

# ▶️ Основной цикл по БИНам
def main():
    with open(BIN_FILE, "r") as f:
        bin_list = [line.strip() for line in f if line.strip()]

    driver = init_driver()
    login(driver)

    for bin_value in bin_list:
        print(f"\n🔎 Проверка БИН: {bin_value}")
        try:
            search_company(driver, bin_value)
            if not open_company_profile(driver):
                continue
            go_to_reliability_tab(driver)
            result = check_customs_status(driver)
            print(f"📌 Статус на сайте: {result}")
            driver.back()
            time.sleep(2)
            driver.back()
            time.sleep(2)
        except Exception as e:
            print(f"❗ Ошибка при обработке БИН {bin_value}: {e}")
            continue

    driver.quit()
    print("✅ Завершено.")

# Запуск
if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    # def check_tax_status(driver, bin_value):
    # try:
    #     label = "В списке компаний попавших под налоговую проверку в 1-ом полугодии 2025 года"
    #     xpath = f"//div[contains(@class, 'text-deepblue-900') and contains(.//span, '{label}')]//div[contains(@class, 'flex w-full items-start md:w-fit')]"
    #     status_element = wait_for_element(driver, By.XPATH, xpath)
    #     status_text = status_element.text.strip()
    #     print(f"📌 Найден статус: {status_text}")
    #     logging.info(f"Tax audit status for BIN {bin_value}: {status_text}")
    #     return status_text if status_text in ["Да", "Нет"] else "Не найдено"
    # except Exception as e:
    #     logging.error(f"Error checking tax audit status for BIN {bin_value}: {e}")
    #     print(f"❌ Ошибка при проверке статуса: {e}")
    #     save_screenshot(driver, bin_value, f"debug_tax_status_{bin_value}.png")
    #     return "Ошибка"
    
    
    # def check_customs_status(driver, bin_value):
    # try:
    #     label = "Комплексные выездные таможенные проверки на 1-ое полугодие 2025 года"
    #     xpath = f"//div[contains(@class, 'text-deepblue-900') and contains(.//span, '{label}')]//div[contains(@class, 'flex w-full items-start md:w-fit')]"
    #     status_element = wait_for_element(driver, By.XPATH, xpath)
    #     status_text = status_element.text.strip()
    #     print(f"📌 Найден статус: {status_text}")
    #     logging.info(f"Customs status for BIN {bin_value}: {status_text}")
    #     return status_text if status_text in ["Да", "Нет"] else "Не найдено"
    # except Exception as e:
    #     logging.error(f"Error checking customs status for BIN {bin_value}: {e}")
    #     print(f"❌ Ошибка при проверке статуса: {e}")
    #     save_screenshot(driver, bin_value, f"debug_customs_status_{bin_value}.png")
    #     return "Ошибка"
