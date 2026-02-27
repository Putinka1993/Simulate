# подключимся к api и посмотрим данные

import requests
import pandas as pd
import ast

api_url = "https://b2b.itresume.ru/api/statistics"

params = {
    'client': 'Skillfactory'
    , 'client_key': 'M2MGWS'
    , 'start': '2023-04-01 12:46:47.860798'
    , 'end': '2023-04-02 13:46:47.860798'
}
response = requests.get(api_url, params=params)

data = response.json()
df = pd.DataFrame(data)


# преобразуем строку в словарь
df['passback_dict'] = df['passback_params'].apply(ast.literal_eval)
# уникальный токен клиента
df['oauth_consumer_key'] = df['passback_dict'].apply(lambda x: x.get('oauth_consumer_key', ''))
# ссылка на блок, в котором находится задача в ЛМС
df['lis_result_sourcedid'] = df['passback_dict'].apply(lambda x: x.get('lis_result_sourcedid', ''))
# URL адрес в ЛМС, куда мы шлем оценку
df['lis_outcome_service_url'] = df['passback_dict'].apply(lambda x: x.get('lis_outcome_service_url', ''))
df_selected = df.loc[:, ['lti_user_id', 'oauth_consumer_key', 'lis_result_sourcedid', 'lis_outcome_service_url', 'is_correct', 'attempt_type', 'created_at']]


##############
# загрузка данных в локальную базу данных postgres
# и запись логов в директорию logs


import requests
import pandas as pd
import ast
import psycopg2
from psycopg2 import sql
import logging
import os
from datetime import datetime, timedelta
import time
import sys

# Настройка логирования
def setup_logging():
    """
    Настраивает систему логирования.
    Создает папку logs, если её нет.
    Удаляет логи старше 3 дней.
    """
    # Создаем папку для логов, если её нет
    log_folder = "logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    # Удаляем старые логи (старше 3 дней)
    current_time = datetime.now()
    for filename in os.listdir(log_folder):
        file_path = os.path.join(log_folder, filename)
        if os.path.isfile(file_path):
            # Получаем дату создания файла
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if current_time - file_time > timedelta(days=3):
                os.remove(file_path)
                print(f"Удален старый лог: {filename}")
    
    # Настраиваем формат логов
    log_filename = os.path.join(log_folder, f"{current_time.strftime('%Y-%m-%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Вывод в консоль
        ]
    )
    
    return logging.getLogger(__name__)

# Функция для подключения к базе данных
def create_db_connection():
    """
    Создает подключение к PostgreSQL базе данных.
    """
    try:
        conn = psycopg2.connect(
            host="localhost",  # или ваш хост
            database="postgres",  # название вашей БД
            user="postgres",  # ваш пользователь
            password="postgres",  # ваш пароль
            port="5432"  # стандартный порт PostgreSQL
        )
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return None

# Функция для создания таблицы, если она не существует
def create_table_if_not_exists(conn):
    """
    Создает таблицу для хранения данных, если она ещё не создана.
    """
    try:
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS student_attempts (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            oauth_consumer_key VARCHAR(255),
            lis_result_sourcedid TEXT,
            lis_outcome_service_url TEXT,
            is_correct BOOLEAN,
            attempt_type VARCHAR(50),
            created_at TIMESTAMP,
            created_at_load TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Создаем индекс для ускорения поиска
        CREATE INDEX IF NOT EXISTS idx_user_id ON student_attempts(user_id);
        CREATE INDEX IF NOT EXISTS idx_created_at ON student_attempts(created_at);
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        logger.info("Таблица успешно создана или уже существует")
        
    except Exception as e:
        logger.error(f"Ошибка при создании таблицы: {e}")
        conn.rollback()

# Функция для загрузки данных в базу
def load_to_database(conn, df):
    """
    Загружает обработанные данные в базу данных.
    """
    try:
        cursor = conn.cursor()
        
        # Счетчики для логирования
        inserted_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Валидация данных перед вставкой
                if pd.isna(row['lti_user_id']) or row['lti_user_id'] == '':
                    logger.warning(f"Пропущена запись с пустым user_id на индексе {index}")
                    error_count += 1
                    continue
                
                # Преобразуем is_correct в булево значение или None
                is_correct_val = None
                if pd.notna(row['is_correct']):
                    if str(row['is_correct']).lower() == 'true':
                        is_correct_val = True
                    elif str(row['is_correct']).lower() == 'false':
                        is_correct_val = False
                
                # Вставка данных
                insert_query = """
                INSERT INTO student_attempts 
                (user_id, oauth_consumer_key, lis_result_sourcedid, lis_outcome_service_url, 
                 is_correct, attempt_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    row['lti_user_id'],
                    row['oauth_consumer_key'] if pd.notna(row['oauth_consumer_key']) else None,
                    row['lis_result_sourcedid'] if pd.notna(row['lis_result_sourcedid']) else None,
                    row['lis_outcome_service_url'] if pd.notna(row['lis_outcome_service_url']) else None,
                    is_correct_val,
                    row['attempt_type'] if pd.notna(row['attempt_type']) else None,
                    row['created_at'] if pd.notna(row['created_at']) else None
                ))
                
                inserted_count += 1
                
                # Коммитим каждые 100 записей для оптимизации
                if inserted_count % 100 == 0:
                    conn.commit()
                    logger.info(f"Загружено {inserted_count} записей...")
                    
            except Exception as e:
                logger.error(f"Ошибка при вставке записи на индексе {index}: {e}")
                error_count += 1
                continue
        
        # Финальный коммит
        conn.commit()
        logger.info(f"Загрузка завершена. Загружено: {inserted_count}, Ошибок: {error_count}")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при загрузке данных: {e}")
        conn.rollback()

# Функция для безопасного преобразования строки в словарь
def safe_literal_eval(val):
    """
    Безопасно преобразует строку в словарь.
    В случае ошибки возвращает пустой словарь и логирует предупреждение.
    """
    try:
        if pd.isna(val) or val is None:
            return {}
        return ast.literal_eval(val)
    except (ValueError, SyntaxError) as e:
        logger.warning(f"Не удалось преобразовать строку в словарь: {val[:100]}... Ошибка: {e}")
        return {}
    except Exception as e:
        logger.error(f"Неожиданная ошибка при преобразовании: {e}")
        return {}

def main():
    """
    Основная функция скрипта.
    """
    global logger
    logger = setup_logging()
    
    logger.info("="*50)
    logger.info("НАЧАЛО РАБОТЫ СКРИПТА")
    logger.info("="*50)
    
    start_time = time.time()
    
    # Параметры для API
    api_url = "https://b2b.itresume.ru/api/statistics"
    
    # Можно настроить динамические даты, например, за последний час
    # end_date = datetime.now()
    # start_date = end_date - timedelta(hours=1)
    
    params = {
        'client': 'Skillfactory',
        'client_key': 'M2MGWS',
        'start': '2023-04-01 12:46:47.860798',
        'end': '2023-04-02 13:46:47.860798'
    }
    
    # Шаг 1: Получение данных от API
    logger.info("Шаг 1: Начинаем загрузку данных из API...")
    
    try:
        response = requests.get(api_url, params=params, timeout=150)
        response.raise_for_status()  # Проверяем на HTTP ошибки
        
        logger.info(f"API ответил со статусом: {response.status_code}")
        
    except requests.exceptions.Timeout:
        logger.error("Таймаут при обращении к API")
        return
    except requests.exceptions.ConnectionError:
        logger.error("Ошибка подключения к API")
        return
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP ошибка: {e}")
        return
    except Exception as e:
        logger.error(f"Неизвестная ошибка при обращении к API: {e}")
        return
    
    logger.info("Загрузка из API успешно завершена")
    
    # Шаг 2: Обработка данных
    logger.info("Шаг 2: Начинаем обработку данных...")
    
    try:
        data = response.json()
        logger.info(f"Получено {len(data)} записей из API")
        
        if not data:
            logger.warning("API вернул пустой список. Работа завершена.")
            return
            
        df = pd.DataFrame(data)
        
        # Преобразуем строку в словарь
        logger.info("Преобразуем passback_params в словари...")
        df['passback_dict'] = df['passback_params'].apply(safe_literal_eval)
        
        # Извлекаем нужные поля
        df['oauth_consumer_key'] = df['passback_dict'].apply(lambda x: x.get('oauth_consumer_key', ''))
        df['lis_result_sourcedid'] = df['passback_dict'].apply(lambda x: x.get('lis_result_sourcedid', ''))
        df['lis_outcome_service_url'] = df['passback_dict'].apply(lambda x: x.get('lis_outcome_service_url', ''))
        
        # Выбираем нужные колонки
        df_selected = df.loc[:, ['lti_user_id', 'oauth_consumer_key', 'lis_result_sourcedid', 
                                  'lis_outcome_service_url', 'is_correct', 'attempt_type', 'created_at']]
        
        logger.info(f"Обработка данных завершена. Подготовлено {len(df_selected)} записей для загрузки")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {e}")
        return
    
    # Шаг 3: Подключение к базе данных и загрузка
    logger.info("Шаг 3: Подключаемся к базе данных...")
    
    conn = create_db_connection()
    if conn is None:
        logger.error("Не удалось подключиться к базе данных. Завершение работы.")
        return
    
    try:
        # Создаем таблицу, если нужно
        create_table_if_not_exists(conn)
        
        # Загружаем данные
        logger.info("Начинаем загрузку данных в базу...")
        load_to_database(conn, df_selected)
        
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
    finally:
        if conn:
            conn.close()
            logger.info("Подключение к базе данных закрыто")
    
    # Завершение работы
    end_time = time.time()
    execution_time = end_time - start_time
    
    logger.info("="*50)
    logger.info(f"РАБОТА СКРИПТА ЗАВЕРШЕНА")
    logger.info(f"Время выполнения: {execution_time:.2f} секунд")
    logger.info("="*50)

if __name__ == "__main__":
    main()


################
# ЗАДАНИЕ СО ЗВЕЗДОЧКОЙ *

# загрузить агрегированные данные в GOOGLE SHEETS 

# Добавьте в ваш скрипт код, который в конце будет агрегировать данные за день

# сколько попыток было совершено;

# сколько успешных попыток было из всех совершенных;

# количество уникальных юзеров;

# процент успеха;

# По типам попыток;

# По дням;


import pandas as pd
from datetime import datetime

# 1. Всего попыток
total_attempts = len(df_selected)
print(f"Всего попыток: {total_attempts}")

# 2. Успешные попытки (is_correct = True)
successful = df_selected['is_correct'].dropna()  # убираем NaN
successful_count = (successful == True).sum()  # или successful.astype(bool).sum()
print(f"Успешных попыток: {successful_count}")

# 3. Уникальных пользователей
unique_users = df_selected['lti_user_id'].nunique()
print(f"Уникальных пользователей: {unique_users}")

# 4. процент успеха
if total_attempts > 0:
    success_rate = (successful_count / total_attempts) * 100
    print(f"Процент успеха: {success_rate:.2f}%")

# 5. По типам попыток
print("\nПо типам попыток:")
print(df_selected['attempt_type'].value_counts())

# 6. По дням
df_selected['created_at'] = pd.to_datetime(df_selected['created_at'])
print("\nПо дням:")
print(df_selected.groupby(df_selected['created_at'].dt.date).size())

# Убедимся, что created_at в правильном формате
df_selected['created_at'] = pd.to_datetime(df_selected['created_at'])

# Основные метрики
total_attempts = len(df_selected)
successful_attempts = df_selected['is_correct'].dropna().astype(bool).sum()
unique_users = df_selected['lti_user_id'].nunique()

# Детальные метрики
attempts_by_type = df_selected['attempt_type'].value_counts()
attempts_by_day = df_selected.groupby(df_selected['created_at'].dt.date).size()
success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0

# Создаем красивый датафрейм для вывода
summary_data = {
    'Показатель': [
        'Всего попыток',
        'Успешных попыток',
        'Уникальных пользователей',
        'Процент успеха (%)',
        'Попыток типа run',
        'Попыток типа submit',
        'Дата начала',
        'Дата окончания'
    ],
    'Значение': [
        total_attempts,
        successful_attempts,
        unique_users,
        round(success_rate, 2),
        attempts_by_type.get('run', 0),
        attempts_by_type.get('submit', 0),
        df_selected['created_at'].min().strftime('%Y-%m-%d %H:%M'),
        df_selected['created_at'].max().strftime('%Y-%m-%d %H:%M')
    ]
}

print("\n Сводка по данным:")
print(f"• Всего попыток: {total_attempts}")
print(f"• Успешных: {successful_attempts}")
print(f"• Уникальных юзеров: {unique_users}")
print(f"• Процент успеха: {success_rate:.2f}%")
print(f"• Run попыток: {attempts_by_type.get('run', 0)}")
print(f"• Submit попыток: {attempts_by_type.get('submit', 0)}")
print(f"• Период: с {df_selected['created_at'].min()} по {df_selected['created_at'].max()}")



################ 
# загрузки данных через сервис аккаунт

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import pandas as pd

# Путь к JSON-файлу
JSON_FILE = '/Users/vladislavlipkin/Downloads/service_account.json'
# ID вашей таблицы (из URL)
SPREADSHEET_ID = '1_WS0RpGbq6kwAk4_sPfX405nnN5Xm6irGEEPFXuf4ew'
# Название листа для сводки
WORKSHEET_NAME = 'Summary'

def upload_summary_to_google_sheets(df_summary):
    """
    Загружает сводный датафрейм в Google Sheets
    """
    print("="*50)
    print(" ЗАГРУЗКА СВОДНЫХ ДАННЫХ В GOOGLE SHEETS")
    print("="*50)
    
    # Проверяем наличие файла с credentials
    if not os.path.exists(JSON_FILE):
        print(f"Файл {JSON_FILE} не найден!")
        return False
    
    print(f" Файл {JSON_FILE} найден")
    
    try:
        # Настраиваем область доступа
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        print(" Авторизация...")
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
        client = gspread.authorize(creds)
        
        # Открываем таблицу
        print(f" Открываем таблицу...")
        sheet = client.open_by_key(SPREADSHEET_ID)
        print(f" Таблица найдена: {sheet.title}")
        
        # Создаем или очищаем лист для сводки
        try:
            worksheet = sheet.worksheet(WORKSHEET_NAME)
            worksheet.clear()
            print(f"Лист '{WORKSHEET_NAME}' очищен")
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=WORKSHEET_NAME, rows=100, cols=10)
            print(f" Создан новый лист: '{WORKSHEET_NAME}'")
        
        # ===== ИСПРАВЛЕНИЕ: преобразуем все значения в строки =====
        # Создаем копию и конвертируем всё в строки
        df_clean = df_summary.copy()
        
        # Конвертируем каждый столбец в строковый тип
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str)
        
        # Подготавливаем данные для загрузки
        data = [df_clean.columns.values.tolist()] + df_clean.values.tolist()
        
        # Добавляем пустую строку и время обновления (тоже строки)
        update_time = [['', ''], ['last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]
        data.extend(update_time)
        
        # Загружаем данные
        worksheet.update(data, value_input_option='USER_ENTERED')
        
        print(f" Данные загружены! Строк: {len(df_summary)}")
        print(f"   Лист: {WORKSHEET_NAME}")
        print(f"   URL: {sheet.url}")
        
        # Показываем первые строки загруженных данных
        print("\n Загруженные данные:")
        print(df_summary.to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f" Ошибка: {e}")
        return False

# Запускаем загрузку
success = upload_summary_to_google_sheets(df_summary)

if success:
    print("\n Готово! Сводные данные загружены в Google Sheets")
else:
    print("\n Что-то пошло не так")






