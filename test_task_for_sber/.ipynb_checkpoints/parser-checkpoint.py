from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Настройки
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)
driver.get("https://kad.arbitr.ru/")

time.sleep(3)

# Поле ввода ИНН
inn_input = driver.find_element(By.CSS_SELECTOR, "#sug-participants > div > textarea")
inn_input.send_keys("7736323532")

# Кнопка поиска
search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
search_button.click()

time.sleep(5)

# Сохраняем результат в файл
html = driver.page_source
with open("result.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Готово! Результат сохранен в result.html")

driver.quit()