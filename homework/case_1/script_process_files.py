# знаю что одно из условий было решить методами которые были разобраны в Глава 9: «Базовая работа с файлами» , но так как владею знания в библиотеки PANDAS то решил делать на pandas.

import glob
import csv
import re
import pandas as pd
import os


def process_files(src_folder, dest_folder):
  csv_files = glob.glob(src_folder + '/*.csv')

  all_df = []

  for csvfile in csv_files:
    if re.search(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d+.csv', csvfile):

      df = pd.read_csv(csvfile, delimiter=';')
      filter_df = df.loc[:, ['date', 'product', 'store', 'cost']]
      all_df.append(filter_df)


  if all_df:
    all_check = pd.concat(all_df, ignore_index=True)

  all_check_sorted = all_check.sort_values(by=['date', 'product'], ascending=[True, True]).reset_index(drop=True)

  os.makedirs(dest_folder, exist_ok=True)

  all_check_sorted.to_csv(
        f'{dest_folder}/combined_data.csv',
        sep=',',
        index=False,
        encoding='utf-8'
    )