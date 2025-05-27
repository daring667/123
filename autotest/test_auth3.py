import pytest
from playwright.sync_api import Page, expect
def test_login(page: Page):
    page.goto("https://id.adata.kz/login")
    
    # Заполняем форму
    page.fill("#email", "test@example.com")
    page.fill("#password", "SecurePass123!")
    page.click("#rememberMe")  # Галочка "Запомнить меня" (опционально)
    page.click("#submit")
    
    # Проверяем, что авторизация прошла
    expect(page).to_have_url("https://id.adata.kz/dashboard")
    expect(page.locator(".user-email")).to_contain_text("test@example.com")