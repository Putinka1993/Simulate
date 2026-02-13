import pandas as pd
import ast




# Задача 1
# Ваша задача написать функцию get_time_to_conversion, которая принимает на вход сессии в формате, который вы определили для себя и подсчитывает среднее время между заходом на сайт и целевым действием.

# Результат - число типа float, округленное до двух знаков после запятой, сохраните в переменную res


path_file = 'sessions.csv'

def get_time_to_conversion(file_csv):
  df = pd.read_csv(file_csv)

  df['session_data'] = df['session'].apply(ast.literal_eval)

  df['session_start'] = df['session_data'].apply(lambda x: x[0])
  df['session_duration'] = df['session_data'].apply(lambda x: x[1])
  df['events'] = df['session_data'].apply(lambda x: x[2])

  df['session_start'] = pd.to_datetime(df['session_start'])

  df_exploded = df.explode('events').reset_index(drop=True)

  df_exploded['page'] = df_exploded['events'].apply(lambda x: x[0])
  df_exploded['event_time'] = df_exploded['events'].apply(lambda x: x[1])
  df_exploded['event_time'] = pd.to_datetime(df_exploded['event_time'])

  df_prepared = df_exploded[['user_id', 'session_start', 'session_duration', 'page', 'event_time']]

  conversion_df = df_prepared[df_prepared['page'] == 'conversion'].copy()

  conversion_df['time_to_conversion'] = (conversion_df['event_time'] - conversion_df['session_start']).dt.total_seconds()

  res = round(conversion_df['time_to_conversion'].mean(), 2)

  return res

res = get_time_to_conversion(path_file)



# Задача 2
# Ваша задача написать функцию get_session_duration, которая принимает на вход сессии в формате, который вы определили для себя и подсчитывает сколько вообще в среднем длится сессия.

# Результат - число типа float, округленное до двух знаков после запятой, сохраните в переменную res2


path_file = 'sessions.csv'

def get_session_duration(file_csv):

  df = pd.read_csv(file_csv)

  df['session_data'] = df['session'].apply(ast.literal_eval)

  df['session_start'] = df['session_data'].apply(lambda x: x[0])
  df['session_duration'] = df['session_data'].apply(lambda x: x[1])
  df['events'] = df['session_data'].apply(lambda x: x[2])

  df['session_start'] = pd.to_datetime(df['session_start'])

  df_exploded = df.explode('events').reset_index(drop=True)

  df_exploded['page'] = df_exploded['events'].apply(lambda x: x[0])
  df_exploded['event_time'] = df_exploded['events'].apply(lambda x: x[1])
  df_exploded['event_time'] = pd.to_datetime(df_exploded['event_time'])

  df_prepared = df_exploded[['user_id', 'session_start', 'session_duration', 'page', 'event_time']]

  res2 = df['session_duration'].mean()
  res2 = round(res2, 2)
  return res2


res2 = get_session_duration(path_file)
res2



# Задача 3
# Напишите функцию get_daily_session_count, которая принимает на вход сессии в формате, который вы определили для себя и подсчитывает cколько разных заходов в течение дня делает пользователь.

# Результат - число типа float, округленное до двух знаков после запятой, сохраните в переменную res3


path_file = 'sessions.csv'

def get_daily_session_count(file_csv):
    df = pd.read_csv(file_csv)
    
    df['session_data'] = df['session'].apply(ast.literal_eval)
    
    df['session_start'] = df['session_data'].apply(lambda x: x[0])
    df['session_start'] = pd.to_datetime(df['session_start'])
    
    df['date'] = df['session_start'].dt.date
    
    daily_sessions = df.groupby(['user_id', 'date'])['user_id'].count()

    return round(daily_sessions.mean(), 2)


res3 = get_daily_session_count(path_file)
res3



# Задача 4
# Напишите функцию get_average_session_count, которая принимает на вход сессии в формате, который вы определили для себя и подсчитывает сколько заходов вообще в среднем делает пользователь.

# Результат - число типа float, округленное до двух знаков после запятой, сохраните в переменную res4


path_file = 'sessions.csv'

def get_average_session_count(file_csv):


  df = pd.read_csv(file_csv)

  df['session_data'] = df['session'].apply(ast.literal_eval)

  df['session_start'] = df['session_data'].apply(lambda x: x[0])
  df['session_duration'] = df['session_data'].apply(lambda x: x[1])
  df['events'] = df['session_data'].apply(lambda x: x[2])

  df['session_start'] = pd.to_datetime(df['session_start'])

  df_exploded = df.explode('events').reset_index(drop=True)

  df_exploded['page'] = df_exploded['events'].apply(lambda x: x[0])
  df_exploded['event_time'] = df_exploded['events'].apply(lambda x: x[1])
  df_exploded['event_time'] = pd.to_datetime(df_exploded['event_time'])

  df_prepared = df_exploded[['user_id', 'session_start', 'session_duration', 'page', 'event_time']]
  df_prepared['date'] = pd.to_datetime(df_prepared['session_start']).dt.date

  df_groupby_user = df_prepared.groupby(['user_id']).agg({'session_start': 'nunique'})

  return round(df_groupby_user['session_start'].mean(), 2)

res4 = get_average_session_count(path_file)
res4





