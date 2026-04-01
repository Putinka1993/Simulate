from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=options)
driver.get("https://kad.arbitr.ru/")

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sug-participants > div > textarea")))

inn_input = driver.find_element(By.CSS_SELECTOR, "#sug-participants > div > textarea")
inn_input.send_keys("7736323532")

search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
search_button.click()

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#b-cases tbody tr")))

data = []
page = 1

while True:
    print(f"Страница {page}")
    rows = driver.find_elements(By.CSS_SELECTOR, "#b-cases tbody tr")
    
    for row in rows:
        try:
            case_link = row.find_element(By.CSS_SELECTOR, "td.num a")
            case_number = case_link.text
            case_url = case_link.get_attribute("href")
            case_id = case_url.split("/")[-1]
            
            data.append({
                "Номер судебного дела": case_number,
                "Системный номер документа": case_id
            })
        except:
            continue
    
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "#pages li.rarr a")
        next_btn.click()
        time.sleep(2)
        page += 1
    except:
        break

driver.quit()

df = pd.DataFrame(data)
df.to_csv("cases.csv", index=False, encoding="utf-8-sig")
print(f"Готово! Собрано {len(df)} дел")