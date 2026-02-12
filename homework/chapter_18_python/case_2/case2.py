import pandas as pd

# Задача 1
# Ваша задача - выяснить сколько в среднем тратится времени на решение задачи.

# Примечание: для правильного подсчета - рассчитайте сначала среднее время решения по каждой задаче в отдельности, и только затем находите общее среднее время решения задач.

# Результат - число типа float, округлите до 2 знаков после запятой и запишите в переменную res.

# море решение , но не дотягивает 10 едениц 
df['created_at'] = pd.to_datetime(df['created_at'])

df_is_not_correct = df.query('is_correct != 1.0')
df_is_not_correct_groupby = df_is_not_correct.groupby(['user_id', 'problem_id']).agg(min_date=('created_at', 'min'))

df_is_correct = df.query('is_correct == 1.0')
df_is_correct_groupby = df_is_correct.groupby(['user_id', 'problem_id']).agg(min_date_main=('created_at', 'min'))

merged_df_inner = pd.merge(df_is_not_correct_groupby, df_is_correct_groupby, on=['user_id', 'problem_id'])

merged_df_inner['diff_seconds'] = (pd.to_datetime(merged_df_inner['min_date_main']) - pd.to_datetime(merged_df_inner['min_date'])).dt.total_seconds()

df_groupby_problem = merged_df_inner.groupby('problem_id').agg({'diff_seconds': 'mean'})
res = float(round(df_groupby_problem.mean().iloc[0], 2))
res

# ответ 596.99

# эталонный ответ
import csv
from collections import defaultdict
import itertools
import datetime

filename = "codesubmit.csv"

rows = []
with open(filename, 'r') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=';')
    for row in csvreader:
        rows.append(row)

# группируем данные по юзеру и проблеме

grouped_data = defaultdict(dict)
for (user_id, problem_id), group in itertools.groupby(rows, lambda x: (x['user_id'], x['problem_id'])):
    for item in group:
        # Создаем новый словарь со всеми соответствующими ключами
        data_dict = {'created_at': item['created_at'], 'is_correct': item['is_correct'], 'type': item['type']}

        grouped_data[user_id].setdefault(problem_id, []).append(data_dict)

# отфильтровываем отлько тех юзеров и проблемы которые в итоге были решены и заодно сортируем
result = defaultdict(dict)
for user_id, problems in grouped_data.items():
    for problem_id, submissions in problems.items():
        sorted_submissions = sorted(submissions, key=lambda x: x['created_at'], reverse=False)
        for submission in sorted_submissions:
            if submission['is_correct'] == '1':
                result[user_id][problem_id] = sorted_submissions
                break

# смотрим сколько врмени прошло от первого рана до правильного решения

result1 = defaultdict(dict)
for user_id, problems in result.items():
    for problem_id, submissions in problems.items():
        time_spent = 0
        prev_time = None
        for submission in submissions:
            if submission['is_correct'] == '1':
                current_time = datetime.datetime.strptime(submission['created_at'], '%Y-%m-%d %H:%M:%S.%f')
                if prev_time:
                    time_spent += round((current_time - prev_time).total_seconds(), 2)
                prev_time = None
                result1[user_id][problem_id] = time_spent
                break
            else:
                current_time = datetime.datetime.strptime(submission['created_at'], '%Y-%m-%d %H:%M:%S.%f')
                if prev_time:
                    time_spent += round((current_time - prev_time).total_seconds(), 2)
                prev_time = current_time
        else:
            result1[user_id][problem_id] = time_spent
# считаем среднее время решения по каждо проблеме причем если время ==0 заносим их в отдельный список

zero_time_problems = []
time_spent = defaultdict(dict)

# Проходим по каждому юзеру и задаче
for user, problems in result1.items():
    for problem, time in problems.items():
        # Проверяем, что потраченное время ненулевое
        if time == 0:
            zero_time_problems.append((user, problem))
        else:
            # Добавляем потраченное время к общему времени на эту задачу
            time_spent[problem]['total_time'] = time_spent[problem].get('total_time', 0) + time
            # Увеличиваем счетчик задачи
            time_spent[problem]['count'] = time_spent[problem].get('count', 0) + 1

# Считаем среднее время по каждой проблеме
average_time_spent = {}
for problem, value in time_spent.items():
    average_time_spent[problem] = value['total_time'] / value['count']

avg_value = sum(average_time_spent.values()) / len(average_time_spent)

res = round(avg_value, 2)


# Задача 2
# Ваша задача - выяснить сколько часов в среднем проводит юзер в день на платформе. Перерывы в активности за день - не учитываем.

# Результат - число типа float, округлите до 2 знаков после запятой и запишите в переменную res2.

df['date'] = pd.to_datetime(df['created_at']).dt.date
df_groupby_user_date = df.groupby(['user_id', 'date']).agg(max_date=('created_at', 'max'), min_date=('created_at', 'min'))
df_groupby_user_date['diff_minutes'] = (df_groupby_user_date['max_date'] - df_groupby_user_date['min_date']).dt.total_seconds() / 3600
df_groupby_user_date.sort_values(by=['user_id', 'date'], ascending=[True, True])
res2 = round(df_groupby_user_date['diff_minutes'].mean(), 2)
res2

# ответ np.float64(1.7)


# Задача 3
# Теперь давайте посмотрим на активные сеансы. Выясните, сколько задач в среднем решается за один активный сеанс.

# Активный сеанс - период, когда между любой активностью пользователя разница менее или равна часу, не более

# Важно: в расчет берем не только успешные попытки решений (is_correct=1), а и неуспешные тоже (is_correct=0), и тип run в том числе.

# Результат - число типа float, округлите до 2 знаков после запятой и запишите в переменную res3.


# мое решение , ну опять не хватает пару сотых

df = df.sort_values(['user_id', 'created_at'])

df['diff_minute'] = df.groupby('user_id')['created_at'].diff().dt.total_seconds() / 60

df['new_session'] = (df['diff_minute'] > 60) | (df['diff_minute'].isna())
df['session_id'] = df.groupby('user_id')['new_session'].cumsum()

session_stats = df.groupby(['user_id', 'session_id'])['problem_id'].nunique()

res3 = round(session_stats.mean(), 2)
res3

# ответ np.float64(3.2)


# эталоное решение 

import datetime
from datetime import timedelta

rows.sort(key=lambda x: (x['user_id'], x['created_at']))

dates_by_user = {}
for row in rows:
    user_id = row['user_id']
    problem_id = row['problem_id']
    created_at = datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S.%f')
    if user_id not in dates_by_user:
        dates_by_user[user_id] = []
    dates_by_user[user_id].append((created_at, problem_id))

results = {}

for user, submissions in dates_by_user.items():
    sessions = []
    current_session = []

    for i in range(len(submissions)):
        if i == 0:
            current_session.append(submissions[i])
        else:
            time_diff = submissions[i][0] - submissions[i-1][0]
            if time_diff > timedelta(hours=1):
                sessions.append(current_session)
                current_session = [submissions[i]]
            else:
                current_session.append(submissions[i])

    # Добавляем последнюю сессию
    sessions.append(current_session)

    # Считаем количество уникальных решенных задач для каждой сессии
    unique_problems = []
    for session in sessions:
        for submission in session:
            problem_id = submission[1]
            if problem_id not in unique_problems:
                unique_problems.append(problem_id)
        session_count = len(unique_problems)
        unique_problems = []

        # Сохраняем результаты
        if user not in results:
            results[user] = {'sessions': 0, 'problems_solved_per_session': []}

        results[user]['sessions'] += 1
        results[user]['problems_solved_per_session'].append(session_count)

total_sessions = 0
total_problems_solved = 0

for user in results:
    sessions = results[user]['sessions']
    problems_solved = sum(results[user]['problems_solved_per_session'])

    total_sessions += sessions
    total_problems_solved += problems_solved

average_problems_solved_per_session = total_problems_solved / total_sessions

res3 = round(average_problems_solved_per_session, 2)



# Задача 4
# И финальная - найдите самый "популярный" час дня на нашей платформе.

# Популярность определяем максимальным количеством уникальных пользователей, совершающих какую-либо активность в этот период

# Результат в числовом формате запишите в переменную res4.

# Например, самым популярным часом стал период с 22 до 23, тогда в переменной res4 должно лежать 22. Обозначающее начало этого периода.

df['hour'] = pd.to_datetime(df['created_at']).dt.hour

hourly_users = df.groupby('hour')['user_id'].nunique()
res4 = hourly_users.idxmax()
res4

# ответ np.int32(16)










