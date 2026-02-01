# решал через pandas

import pandas as pd

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Указываем необходимые права доступа к таблицам
scope = ['https://www.googleapis.com/auth/spreadsheets.readonly',
         'https://www.googleapis.com/auth/drive']

# Загружаем ключи аутентификации из файла json
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

# Авторизуемся в Google Sheets API
client = gspread.authorize(creds)


sheet_1 = client.open("Installments").worksheet("Лист1")
sheet1_data = sheet_1.get_all_records()

sheet_2 = client.open("Installments").worksheet("Лист2")
sheet2_data = sheet_2.get_all_records()

sheet_3 = client.open("Installments").worksheet("Лист3")
sheet3_data = sheet_3.get_all_records()



def generate_report(sheet1, sheet2, sheet3):

  # преобразуем excel в DataFrame
  students_info_1 = pd.DataFrame(sheet1_data)
  payment_schedule_2 = pd.DataFrame(sheet2_data)
  installment_balance_3 = pd.DataFrame(sheet3_data)

  # оставим студентов которые имеет рассрочку
  students_info_1 = students_info_1.query('installment == "Y"')

  # соеденим все 3 таблицы в одну единую таблицу
  all_table = students_info_1.merge(
      payment_schedule_2, on='student_id').merge(
          installment_balance_3, on='student_id')

  # отсеем лишнее, оставим поля с которыми будем работать
  filter_table = all_table.loc[:,['student_name', 'last_payment_date', 'expected_payment_date', 'already_payed_amount', 'left_to_pay', 'one-time_payment', 'installment_amount']]

  # преобразуем строки с датой в datetime
  filter_table['last_payment_date'] = pd.to_datetime(filter_table['last_payment_date'], format='%d.%m.%Y')
  filter_table['expected_payment_date'] = pd.to_datetime(filter_table['expected_payment_date'], format='%d.%m.%Y')

  # посчитаем разницу дней от требуемой даты и даты последнего платежа
  fixed_date = pd.to_datetime('2023-03-01')
  filter_table['diff_days'] = (filter_table['expected_payment_date'] - fixed_date).dt.days

  # еще раз отберем требуемые данные для анализа
  filter_table = filter_table.loc[:,['student_name', 'last_payment_date', 'expected_payment_date', 'diff_days',  'already_payed_amount', 'left_to_pay', 'installment_amount', 'one-time_payment']]

  # определим должников где есть отрицательная разница дней ,
  # эту строчку debtors['overdue_count'] = ((abs(debtors['diff_days']) + 182) // 183).clip(lower=0)
  # я частично написал с помощью Chat GPT))
  # поле ['debt'] , мы считаем количество просрочек умноженное на разовый платеж , 
  # но при условии что сумма не будет превышать остатка долга (left_to_pay).
  debtors = filter_table.query('diff_days < 0')
  debtors['overdue_count'] = ((abs(debtors['diff_days']) + 182) // 183).clip(lower=0)
  debtors['debt'] = debtors['one-time_payment'] * debtors['overdue_count']

  # здесь все просто , проходимся по фреймам и проверяем условие выше описанное.
  result = []
  for name, debt, left_to_pay in zip(debtors['student_name'], debtors['debt'], debtors['left_to_pay']):
    if debt < left_to_pay:
      print(f'Студент {name} - долг {debt}')
      result.append(f'Студент {name} - долг {debt} рублей')
    else:
      print(f'Студент {name} - долг {left_to_pay}')
      result.append(f'Студент {name} - долг {left_to_pay} рублей')

  # тоже подсказал Chat GPT , так как в конце результата была лишняя строка, 
  # ну мне кажется это было не столько важно
  result = '\n'.join(result)

  # записываем результат , и все готово!
  with open('student_debt_report.txt', 'w', encoding='utf-8') as txtfile:
    txtfile.write(result)


# generate_report(sheet1_data, sheet2_data, sheet3_data)
