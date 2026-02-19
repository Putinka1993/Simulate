import pandas as pd


# Задача 1
# Ваша задача написать класс Extraction, и определить в нем метод from_csv, который принимал бы путь к файлу и вытаскивал данные в виде списка объектов.

# Для этого, здесь же, определите класс Sale.

# Класс (Sale)
class Sale:
    def __init__(self, sale_id, date, amount, product):
        self._id = sale_id
        self._date = date
        self._amount = amount
        self._product = product

    def get_id(self):
        return self._id

    def get_date(self):
        return self._date

    def get_amount(self):
        return self._amount

    def get_product(self):
        return self._product



# Класс (Extraction)
class Extraction:
    @staticmethod
    def from_csv(file_path):
        df = pd.read_csv(file_path)
        
        df['amount'] = pd.to_numeric(df['amount'])
        
        sales_data = []
        for _, row in df.iterrows():
            sale = Sale(
                sale_id=row['id'],
                date=row['date'],
                amount=row['amount'],
                product=row['product']
            )
            sales_data.append(sale)
        
        return sales_data

# Задача 2
# Напишите класс Transformation, который содержит два метода: filter_by_date(sales_data, start_date, end_date) и filter_by_amount(sales_data, min_amount, max_amount)

# Класс "Преобразование" (Transformation)
class Transformation:
    @staticmethod
    def filter_by_date(sales_data, start_date, end_date):
        filtered_sales = []
        for sale in sales_data:
            if start_date <= sale.get_date() <= end_date:
                filtered_sales.append(sale)
        return filtered_sales

    @staticmethod
    def filter_by_amount(sales_data, min_amount, max_amount):
        filtered_sales = []
        for sale in sales_data:
            if min_amount <= sale.get_amount() <= max_amount:
                filtered_sales.append(sale)
        return filtered_sales


# Задача 3
# Напишите класс Analysis, содержащий два метода: calculate_total_sales и calculate_average_sales. Возвращаемые значения округлите до двух знаков после запятой.


class Analysis:
    @staticmethod
    def calculate_total_sales(sales_data):
        total = sum(sale.get_amount() for sale in sales_data)
        return round(total, 2)
    
    @staticmethod
    def calculate_average_sales(sales_data):
        if not sales_data:  # защита от пустого списка
            return 0.0
        
        total = sum(sale.get_amount() for sale in sales_data)
        average = total / len(sales_data)
        return round(average, 2)


# Задача 4
# Напишите класс Loading с методом to_csv(sales_data, file_path), который запишет данные в csv файл.

# Класс "Загрузка" (Loading)
class Loading:
    @staticmethod
    def to_csv(sales_data, file_path):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'date', 'amount', 'product'])
            for sale in sales_data:
                writer.writerow([sale.get_id(), sale.get_date(), sale.get_amount(), sale.get_product()])







