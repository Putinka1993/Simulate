import pandas as pd
import os
import webbrowser
from datetime import datetime
from jinja2 import Template

# чтение excel
file_path = "source.xlsx"
sheet_name = "Ведомость объемов работ 6 граф"

df = pd.read_excel(
    file_path,
    sheet_name=sheet_name,
    header=None,
    skiprows=13,
    nrows=7
)

# очистка данных
works_list = []
for idx, row in df.iterrows():
    name = row[1] if pd.notna(row[1]) else ""
    if not name:
        continue
    
    qty_raw = str(row[3]) if pd.notna(row[3]) else "0"
    qty_clean = qty_raw.replace('"', '').replace('\n', '').replace(',', '.').strip()
    try:
        qty = float(qty_clean)
    except:
        qty = 0.0
    
    works_list.append({
        "name": name,
        "qty": qty
    })

# цены
prices = [
    {"keyword": "С 245", "material_price": 55000, "work_price": 35000},
    {"keyword": "С 345", "material_price": 60000, "work_price": 35000},
    {"keyword": "профнастила", "material_price": 850, "work_price": 400},
    {"keyword": "Абразивоструйная", "material_price": 150, "work_price": 200},
    {"keyword": "Огрунтовка", "material_price": 100, "work_price": 80},
    {"keyword": "эмалью", "material_price": 250, "work_price": 170},
    {"keyword": "огнезащитным", "material_price": 720, "work_price": 360},
]

# расчёт
results = []
for work in works_list:
    name = work["name"]
    qty = work["qty"]
    
    material_price = 0
    work_price = 0
    for p in prices:
        if p["keyword"] in name:
            material_price = p["material_price"]
            work_price = p["work_price"]
            break
    
    material_total = qty * material_price
    work_total = qty * work_price
    total = material_total + work_total
    
    results.append({
        "name": name,
        "qty": qty,
        "material_price": material_price,
        "work_price": work_price,
        "material_total": material_total,
        "work_total": work_total,
        "total": total
    })

# общая сумма
grand_total = sum(r["total"] for r in results)

# html шаблон
html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Смета на основе BIM-данных</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .date {
            text-align: right;
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: bold;
        }
        td {
            padding: 10px;
            text-align: right;
            border-bottom: 1px solid #ddd;
        }
        td:first-child, td:nth-child(2) {
            text-align: left;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .grand-total {
            font-size: 20px;
            font-weight: bold;
            text-align: right;
            margin-top: 20px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 8px;
            color: #27ae60;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #95a5a6;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Смета на основе BIM-данных</h1>
        <div class="date">{{ date }}</div>
        
        <table>
            <thead>
                <tr>
                    <th>№</th>
                    <th>Наименование работ</th>
                    <th>Кол-во</th>
                    <th>Ед. изм.</th>
                    <th>Материал (руб)</th>
                    <th>Работа (руб)</th>
                    <th>Итого (руб)</th>
                </tr>
            </thead>
            <tbody>
                {% for item in results %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ item.name }}</td>
                    <td>{{ "%.3f"|format(item.qty) }}</td>
                    <td>
                        {% if 'м2' in item.name.lower() or 'профнастил' in item.name.lower() %}
                            м²
                        {% else %}
                            т
                        {% endif %}
                    </td>
                    <td>{{ "%.2f"|format(item.material_total) }}</td>
                    <td>{{ "%.2f"|format(item.work_total) }}</td>
                    <td><strong>{{ "%.2f"|format(item.total) }}</strong></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="grand-total">
            ОБЩАЯ СТОИМОСТЬ: {{ "%.2f"|format(grand_total) }} руб
        </div>
        
        <div class="footer">
            Расчёт выполнен на основе BIM-выгрузки
        </div>
    </div>
</body>
</html>
"""

template = Template(html_template)
html_content = template.render(
    results=results,
    grand_total=grand_total,
    date=datetime.now().strftime("%d.%m.%Y %H:%M:%S")
)

html_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
with open(html_filename, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Отчёт сохранён: {html_filename}")
print(f"Общая стоимость: {grand_total:,.2f} руб")

webbrowser.open(f"file://{os.path.abspath(html_filename)}")