# PS задачи делал с помощью pandas ( знаю что условие делать имеющимеся методами )
import pandas as pd

# 2 кейс
# В этом кейсе вы будете рассчитывать:

# самую эффективную платформу
# самый успешный тип рекламной кампании
# географию
# рекламные расходы по городам
# даты, в которые не запускались кампании
# и еще кое-что




# Найдите самую эффективную платформу по средним значениям конверсий
# Cохраните результат в переменную most_effective_platform

sales_platforms = pd.read_csv('campaign_data.csv')

conversion_for_platforms = sales_platforms.groupby('Платформа').agg({'Конверсия': 'mean'})

print(conversion_for_platforms.sort_values(by='Конверсия', ascending=False))

most_effective_platform = conversion_for_platforms['Конверсия'].idxmax()
print(most_effective_platform)



# Найдите самый успешный тип рекламной кампании по средним значениям конверсий
# Сохраните результат в переменную most_successful_campaign_type


sales_platforms = pd.read_csv('campaign_data.csv')

top_company_for_conversion = sales_platforms.groupby('Тип кампании').agg({'Конверсия': 'mean'})
print(top_company_for_conversion.sort_values(by='Конверсия', ascending=False))

most_successful_campaign_type = top_company_for_conversion['Конверсия'].idxmax()
print(most_successful_campaign_type)



# Найдите самый успешный город проведения кампании по средним значениям конверсий
# Сохраните результат в переменную most_successful_city


sales_platforms = pd.read_csv('campaign_data.csv')

top_city_for_conversion = sales_platforms.groupby('Город').agg({'Конверсия': 'mean'})
print(top_city_for_conversion.sort_values(by='Конверсия', ascending=False))

most_successful_city = top_city_for_conversion['Конверсия'].idxmax()
print(most_successful_city)



# Посчитайте долю затрат на рекламные кампании каждой платформы и каждого города
# Сохраните результат в файл platform_city_results.txt

# Результат должен иметь такой же порядок групп, что и изначальный файл. А города внутри платформ должны быть отсортированы по убыванию доли затрат, а доля затрат должны быть округлена до 2 знаков после запятой.


sales_platforms = pd.read_csv('campaign_data.csv')

budget_by_company = sales_platforms.groupby(['Платформа', 'Город']).agg({'Бюджет': 'sum'})

budget_by_company['share'] = round(budget_by_company['Бюджет'] / budget_by_company.groupby('Платформа')['Бюджет'].sum() * 100.0, 2)

result = budget_by_company['share']

unique_platforms = sales_platforms['Платформа'].unique()


# создадим словарь ( что бы отсортировать внутри списков по доле )
result_dict = {key: [] for _, key in enumerate(unique_platforms)}
for (platform, city), share in result.items():
  result_dict[platform].append((city, share))

for platform in result_dict:
    result_dict[platform].sort(key=lambda x: x[1], reverse=True)

for platform in unique_platforms:
  print(f'Для группы {platform}:')
  for city, share in result_dict[platform]:
    print(f'- Город: {city}, доля затрат на рекламу: {share}%')

with open('platform_city_results.txt', 'w', encoding='utf-8') as f:
    for platform in unique_platforms:
        f.write(f'Для группы {platform}:\n')
        for city, share in result_dict[platform]:
            f.write(f'- Город: {city}, доля затрат на рекламу: {share}%\n')



# Напишите функцию, которая возвращает средний бюджет всех кампаний, запущенных на определенной платформе
# Функция calculate_average_budget должна принимать путь к файлу и название плафтормы и возвращать число - средний бюджет всех кампаний, запущенных на данной платформе, округленный до двух знаков после запятой.


def calculate_average_budget(file_path, company):
  sales_platforms = pd.read_csv(file_path)

  target_platform = sales_platforms.query(f'Платформа == "{company}"')
  target_platform = target_platform['Бюджет'].mean().round(2)

  return target_platform

calculate_average_budget('campaign_data.csv', 'Google')



# Напишите генератор, который будет генерировать даты, в которые НЕ запускались кампании
# Функция get_missing_campaign_dates должна принимать путь к файлу и генерировать построчно даты, отсортированные по возрастанию, в которые не запускались кампании, в формате:


from datetime import datetime, timedelta, date

def get_missing_campaign_dates(file_path):
    df = pd.read_csv(file_path)
    
    df['Начальная дата'] = pd.to_datetime(df['Начальная дата'])
    start_dates_set = set(df['Начальная дата'].dt.date)
    
    min_date = min(df['Начальная дата']).date()
    max_date = max(df['Начальная дата']).date()
    
    missing_dates = []

    current_date = min_date
    while current_date <= max_date:
        if current_date not in start_dates_set:
            missing_dates.append(current_date)

        current_date += timedelta(days=1)
    
    return missing_dates

result = get_missing_campaign_dates('campaign_data.csv')

get_missing_campaign_dates('campaign_data.csv')



# Напишите функцию, которая будет принимать на вход путь к файлу и возвращать сгруппированные данные по городам, содержащие суммарный бюджет и количество кликов
# Функция group_campaign_data должна возвращать список словарей, отсортированный по городам


def group_campaign_data(file_path):
  df = pd.read_csv(file_path)

  agg_for_city = df.groupby(['Город']).agg({'Бюджет': 'sum', 'Клики': 'sum'})

  result_list = []
  for city, row in agg_for_city.iterrows():
    cash = row['Бюджет']
    clicks = row['Клики']

    result_list.append({'Город': city,'Количество кликов': float(clicks),'Суммарный бюджет': int(cash)})

  result_list = sorted(result_list, key=lambda x: x['Город'])

  return result_list

group_campaign_data('campaign_data.csv')



# Напишите генератор, который будет генерировать данные о кампаниях, запущенных в указанном городе и имеющих бюджет выше заданного значения
# Функция campaign_generator должна принимать путь к файлу, город и бюджет и генерировать словари, отсортированные по возрастанию 'ID Кампании


def campaign_generator(file_path, city, num):
  df = pd.read_csv(file_path)

  revenue_for_city = df.query('Бюджет > @num and Город == @city')
  revenue_for_city = revenue_for_city.loc[:, ['ID Кампании', 'Тип кампании', 'Платформа', 'Доход']]

  result_list = []
  for _, row in revenue_for_city.iterrows():
      result_list.append({
          'ID Кампании': str(row['ID Кампании']),
          'Тип': row['Тип кампании'],
          'Платформа': row['Платформа'],
          'Доход': str(row['Доход'])
      })

  result_list = sorted(result_list, key=lambda x: int(x['ID Кампании']))

  return result_list
    
campaign_generator('campaign_data.csv', 'Казань', 47000)













