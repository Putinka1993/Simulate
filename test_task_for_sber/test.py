from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

# Используем твой профиль Chrome
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--user-data-dir=/Users/vladislavlipkin/Library/Application Support/Google/Chrome")
options.add_argument("--profile-directory=Default")

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
time.sleep(5)

data1 = []
data2 = []
page = 1

while True:
    print(f"Страница {page}")
    rows = driver.find_elements(By.CSS_SELECTOR, "#b-cases tbody tr")
    cases_on_page = []
    
    for row in rows:
        try:
            case_link = row.find_element(By.CSS_SELECTOR, "td.num a")
            case_number = case_link.text
            case_url = case_link.get_attribute("href")
            case_id = case_url.split("/")[-1]
            cases_on_page.append((case_number, case_url, case_id, row))
        except:
            continue
    
    for case_number, case_url, case_id, row in cases_on_page:
        try:
            # Истец
            plaintiff_inn = None
            plaintiff_name = ""
            try:
                plaintiff_elem = row.find_element(By.CSS_SELECTOR, "td.plaintiff .js-rollover")
                tooltip_html = plaintiff_elem.get_attribute("innerHTML")
                inn_match = re.search(r'ИНН:\s*(\d+)', tooltip_html)
                if inn_match:
                    plaintiff_inn = inn_match.group(1)
                name_match = re.search(r'<strong>(.*?)</strong>', tooltip_html)
                if name_match:
                    plaintiff_name = name_match.group(1)
            except:
                pass
            
            # Ответчик
            respondent_inn = None
            respondent_name = ""
            try:
                respondent_elem = row.find_element(By.CSS_SELECTOR, "td.respondent .js-rollover")
                tooltip_html = respondent_elem.get_attribute("innerHTML")
                inn_match = re.search(r'ИНН:\s*(\d+)', tooltip_html)
                if inn_match:
                    respondent_inn = inn_match.group(1)
                name_match = re.search(r'<strong>(.*?)</strong>', tooltip_html)
                if name_match:
                    respondent_name = name_match.group(1)
            except:
                pass
            
            # Переход в карточку
            driver.get(case_url)
            time.sleep(2)
            
            # Статус
            status = ""
            try:
                status_elem = driver.find_element(By.CSS_SELECTOR, ".b-case-header-desc")
                status = status_elem.text.strip()
            except:
                pass
            
            # Сумма требований
            claim_amount = ""
            try:
                claim_elem = driver.find_element(By.CSS_SELECTOR, ".additional-info")
                text = claim_elem.text
                match = re.search(r'Сумма исковых требований\s+([\d\s,]+\.?\d*)', text)
                if match:
                    claim_amount = match.group(1).replace(" ", "")
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
            
            # Предмет спора
            subject = ""
            try:
                subject_elem = driver.find_element(By.CSS_SELECTOR, ".b-case-header i.b-icon + span")
                subject = subject_elem.text.strip()
            except:
                pass
            
        except Exception as e:
            print(f"Ошибка при загрузке карточки {case_number}: {e}")
            status = claim_amount = document_text = chronology_text = subject = ""
        
        # Таблица 1
        data1.append({
            "Номер судебного дела": case_number,
            "Системный номер документа": case_id,
            "ИНН истца": plaintiff_inn,
            "Название истца": plaintiff_name,
            "ИНН ответчика": respondent_inn,
            "Имя ответчика": respondent_name,
            "Статус судебного разбирательства": status,
            "Текст документа": document_text
        })
        
        # Таблица 2
        data2.append({
            "Номер судебного дела": case_number,
            "Предмет судебного разбирательства": subject,
            "Хронология судебного разбирательства": chronology_text,
            "Сумма требований": claim_amount,
            "Сумма возмещения": ""
        })
        
        driver.back()
        time.sleep(1)
    
    # Следующая страница
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "#pages li.rarr a")
        next_btn.click()
        time.sleep(3)
        page += 1
    except:
        print("Все страницы обработаны")
        break

driver.quit()

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

df1.to_csv("table1.csv", index=False, encoding="utf-8-sig")
df2.to_csv("table2.csv", index=False, encoding="utf-8-sig")

print(f"Готово! Таблица 1: {len(df1)} записей, Таблица 2: {len(df2)} записей")