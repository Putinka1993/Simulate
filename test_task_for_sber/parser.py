from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Настройки
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)
driver.get("https://kad.arbitr.ru/")

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sug-participants > div > textarea")))

# Ввод ИНН
inn_input = driver.find_element(By.CSS_SELECTOR, "#sug-participants > div > textarea")
inn_input.send_keys("7736323532")

# Кнопка поиска
search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
search_button.click()

# Ждем загрузки таблицы
time.sleep(5)

# Парсим таблицу
rows = driver.find_elements(By.CSS_SELECTOR, "#b-cases tbody tr")

data = []

for row in rows:
    # Номер дела и ссылка
    case_link = row.find_element(By.CSS_SELECTOR, "td.num a")
    case_number = case_link.text
    case_url = case_link.get_attribute("href")
    case_id = case_url.split("/")[-1]
    
    # Истец
    plaintiff_elem = row.find_element(By.CSS_SELECTOR, "td.plaintiff .js-rollover")
    plaintiff_html = plaintiff_elem.get_attribute("innerHTML")
    
    # Ответчик
    respondent_elem = row.find_element(By.CSS_SELECTOR, "td.respondent .js-rollover")
    respondent_html = respondent_elem.get_attribute("innerHTML")
    
    data.append({
        "case_number": case_number,
        "case_url": case_url,
        "case_id": case_id,
        "plaintiff_html": plaintiff_html,
        "respondent_html": respondent_html
    })

print(f"Найдено дел: {len(data)}")
driver.quit()