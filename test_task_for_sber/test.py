from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import re

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
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#b-cases tbody tr")))

data1 = []
data2 = []
actions = ActionChains(driver)

# Берем первые 3 строки
rows = driver.find_elements(By.CSS_SELECTOR, "#b-cases tbody tr")[:3]

case_links = []

for row in rows:
    try:
        case_link = row.find_element(By.CSS_SELECTOR, "td.num a")
        case_number = case_link.text
        case_url = case_link.get_attribute("href")
        case_id = case_url.split("/")[-1]
        
        # Истец
        plaintiff_inn = None
        plaintiff_name = ""
        try:
            plaintiff_elem = row.find_element(By.CSS_SELECTOR, "td.plaintiff .js-rollover")
            actions.move_to_element(plaintiff_elem).perform()
            time.sleep(0.5)
            
            tooltips = driver.find_elements(By.CSS_SELECTOR, ".b-rollover:not([style*='display: none'])")
            if tooltips:
                tooltip_text = tooltips[0].text
                inn_match = re.search(r'ИНН:\s*(\d+)', tooltip_text)
                if inn_match:
                    plaintiff_inn = inn_match.group(1)
                plaintiff_name = tooltip_text.split("\n")[0]
        except:
            pass
        
        # Ответчик
        respondent_inn = None
        respondent_name = ""
        try:
            respondent_elem = row.find_element(By.CSS_SELECTOR, "td.respondent .js-rollover")
            actions.move_to_element(respondent_elem).perform()
            time.sleep(0.5)
            
            tooltips = driver.find_elements(By.CSS_SELECTOR, ".b-rollover:not([style*='display: none'])")
            if tooltips:
                tooltip_text = tooltips[0].text
                inn_match = re.search(r'ИНН:\s*(\d+)', tooltip_text)
                if inn_match:
                    respondent_inn = inn_match.group(1)
                respondent_name = tooltip_text.split("\n")[0]
        except:
            pass
        
        case_links.append({
            "case_number": case_number,
            "case_url": case_url,
            "case_id": case_id,
            "plaintiff_inn": plaintiff_inn,
            "plaintiff_name": plaintiff_name,
            "respondent_inn": respondent_inn,
            "respondent_name": respondent_name
        })
    except:
        continue

print(f"Собрано {len(case_links)} дел для обработки")

# Проходим по каждой карточке
for idx, case in enumerate(case_links):
    print(f"Обработка карточки {idx+1}/{len(case_links)}: {case['case_number']}")
    
    driver.get(case["case_url"])
    time.sleep(2)
    
    # Статус
    status = ""
    try:
        status_elem = driver.find_element(By.CSS_SELECTOR, ".b-case-header-desc")
        status = status_elem.text.strip()
    except:
        pass
    
    # Предмет спора
    subject = ""
    try:
        subject_elem = driver.find_element(By.CSS_SELECTOR, ".b-iblock__header_card span")
        subject = subject_elem.text.strip()
    except:
        try:
            subject_elem = driver.find_element(By.CSS_SELECTOR, ".b-iblock__header_card .b-icon + span")
            subject = subject_elem.text.strip()
        except:
            pass
    
    # Раскрываем хронологию
    try:
        expand_btn = driver.find_element(By.CSS_SELECTOR, ".b-collapse.js-collapse")
        expand_btn.click()
        time.sleep(1)
    except:
        pass
    
    # Сумма требований
    claim_amount = ""
    try:
        all_additional = driver.find_elements(By.CSS_SELECTOR, ".additional-info")
        for elem in all_additional:
            text = elem.text
            match = re.search(r'Сумма исковых требований\s+([\d\s,]+\.?\d*)', text)
            if match:
                claim_amount = match.group(1).replace(" ", "")
                break
    except:
        pass
    
    # Текст документа (PDF)
    document_text = ""
    try:
        pdf_link = driver.find_element(By.CSS_SELECTOR, ".b-chrono-item .b-case-result a[href*='.pdf']")
        document_text = pdf_link.get_attribute("href")
    except:
        pass
    
    # Хронология
    chronology = []
    try:
        events = driver.find_elements(By.CSS_SELECTOR, ".b-chrono-item")
        for event in events[:20]:
            try:
                date = event.find_element(By.CSS_SELECTOR, ".case-date").text
                event_type = event.find_element(By.CSS_SELECTOR, ".case-type").text
                desc_elem = event.find_element(By.CSS_SELECTOR, ".b-case-result-text")
                desc = desc_elem.text if desc_elem else ""
                chronology.append(f"{date} | {event_type} | {desc}")
            except:
                pass
    except:
        pass
    
    chronology_text = "\n".join(chronology)
    
    data1.append({
        "Номер судебного дела": case["case_number"],
        "Системный номер документа": case["case_id"],
        "ИНН истца": case["plaintiff_inn"],
        "Название истца": case["plaintiff_name"],
        "ИНН ответчика": case["respondent_inn"],
        "Имя ответчика": case["respondent_name"],
        "Статус судебного разбирательства": status,
        "Текст документа": document_text
    })
    
    data2.append({
        "Номер судебного дела": case["case_number"],
        "Предмет судебного разбирательства": subject,
        "Хронология судебного разбирательства": chronology_text,
        "Сумма требований": claim_amount,
        "Сумма возмещения": ""
    })

driver.quit()

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

df1.to_csv("table1.csv", index=False, encoding="utf-8-sig")
df2.to_csv("table2.csv", index=False, encoding="utf-8-sig")

print("\n=== ГОТОВО ===")
print(f"Таблица 1: {len(df1)} записей")
print(df1[["Номер судебного дела", "ИНН истца", "ИНН ответчика", "Статус судебного разбирательства"]])
print("\nТаблица 2:")
print(df2[["Номер судебного дела", "Предмет судебного разбирательства", "Сумма требований"]])