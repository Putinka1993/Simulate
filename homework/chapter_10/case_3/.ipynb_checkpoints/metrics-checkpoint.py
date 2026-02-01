# retention
# rolling retention
# lifetime
# churn rate
# mau
# wau
# dau
# avg_mau
# avg_wau
# avg_dau


import pandas as pd 



# retention_15_day

registrations = pd.read_csv('registrations.csv', delimiter=';') 
entries = pd.read_csv('entries.csv', delimiter=';') 
join_table = entries.merge(registrations, how='left', on='user_id') 
join_table['entry_date'] = pd.to_datetime(join_table['entry_date']) 
join_table['registration_date'] = pd.to_datetime(join_table['registration_date']) 
join_table['day_diff'] = (join_table['entry_date'] - join_table['registration_date']).dt.days 
join_table = join_table.query('registration_date.dt.month == 1') 

retention_15_day = round(len(join_table.query('day_diff == 15')['user_id'].unique()) / len(join_table['user_id'].unique()) * 100.0, 5) 
# 54.65116


# rolling_retention_day_30

join_table = join_table.query('registration_date.dt.month == 1') 
rolling_retention = round(len(join_table.query('day_diff >= 30')['user_id'].unique()) / len(join_table['user_id'].unique()) * 100.0, 5)
# 29.06977


# lifetime

result = join_table.groupby('user_id').agg({'entry_date': 'nunique'})
lifetime = round(result.mean().loc['entry_date'], 5)
# 14.804


# churn_rate_day_29

churn_29 = round(1 - len(join_table.query('day_diff >= 29')['user_id'].unique()) / len(join_table['user_id'].unique()), 5) 
# 0.509


# dec_mau

join_table = join_table.query('entry_date.dt.month == 12')
dec_mau = join_table['user_id'].nunique()
# 133


# dec_wau

#  с 25 по 31 декабря
join_table = join_table.query('"2021-12-25" <= entry_date <= "2021-12-31"')
dec_wau = join_table['user_id'].nunique()
# 84


# dec_31_dau

# 31 december 2021
join_table = join_table.query('"2021-12-31" == entry_date')
dec_dau = join_table['user_id'].nunique()
# 47


# avg_mau

join_table['MONTH'] = join_table['entry_date'].dt.month
result = join_table.groupby('MONTH').agg({'user_id': 'nunique'})

avg_mau = round(result.mean().loc['user_id'], 5)
# 102.58333


# avg_wau

join_table['WEEK'] = join_table['entry_date'].dt.isocalendar().week
result = join_table.groupby('WEEK').agg({'user_id': 'nunique'})

avg_wau = round(result.mean().loc['user_id'], 5)
# 89.86792


# avg_dau

join_table['MONTH'] = join_table['entry_date'].dt.month
join_table['DAY'] = join_table['entry_date'].dt.day
result = join_table.groupby(['MONTH', 'DAY']).agg({'user_id': 'nunique'})

avg_dau = round(result.mean().loc['user_id'], 5)
# 40.5589






