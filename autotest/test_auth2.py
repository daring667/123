import pytest
from playwright.sync_api import Page, expect

def test_registration(page: Page):
    page.goto("https://id.adata.kz/register")
    
    # Вариант 1: Регистрация через email
    page.fill("#email", "test@example.com")
    page.fill("#password", "SecurePass123!")
    page.click("#submit")
    
    # Проверяем успешную регистрацию
    expect(page).to_have_url("https://id.adata.kz/dashboard")  # Или другой URL
    expect(page.locator(".welcome-message")).to_contain_text("Добро пожаловать")

    # Вариант 2: Регистрация через телефон (аналогично)
    # Вариант 3: Через Google (можно mock'ать или использовать тестовый аккаунт)