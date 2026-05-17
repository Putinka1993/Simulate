# ABC Анализ — Конспект

## Что такое ABC анализ?

**ABC анализ** — метод управления товарами, который классифицирует товары на три категории по их вкладу в общий результат (продажи, прибыль, оборачиваемость и т.д.).

Основан на **законе Парето (правило 80/20)**: 
- ~20% товаров дают ~80% результата → это товары категории **A** (самые ценные)
- Следующие ~30% товаров дают ~15% результата → это товары категории **B** (средняя ценность)
- Остальные ~50% товаров дают ~5% результата → это товары категории **C** (низкая ценность)

---

## Границы ABC классификации (по кумулятивному проценту)

| Категория | Кумулятивный процент | Что это означает |
|-----------|---------------------|-----------------|
| **A** | 0% - 80% | Товары, которые накопили 80% результата |
| **B** | 80% - 95% | Товары, которые накопили ещё 15% (с 80% до 95%) |
| **C** | 95% - 100% | Товары, которые накопили оставшиеся 5% |

**Ключевое:** мы смотрим на **кумулятивную сумму**, отсортированную по убыванию метрики.

---

## Многомерный ABC анализ (3 метрики)

Вместо одной метрики (например, только продажи) можно анализировать **несколько метрик одновременно**:

### Три метрики для аптечной сети:

1. **Количество проданных штук** (`amount`)
   - Сколько штук товара продано всего
   - Формула: `SUM(количество единиц)`

2. **Сумма продаж** (`profit_with_discount`)
   - Выручка с учётом скидок
   - Формула: `SUM(цена - скидка)`

3. **Месячная оборачиваемость** (`month_average`)
   - Как часто товар продаётся в месяц (на основе среднего дневного объёма)
   - Формула: `SUM(количество) / COUNT(DISTINCT дни) * 30`

Каждому товару присваиваются **три буквы** (одна для каждой метрики). Например:
- **AAA** — топовый товар по всем трём метрикам
- **ABC** — хороший по количеству и выручке, но медленно оборачивается
- **CCC** — низкая ценность по всем параметрам

---

## Пошаговое решение на SQL

### Шаг 1: Агрегируем данные по товарам

```sql
WITH group_table AS (
  SELECT
    ds.dr_ndrugs,                                    -- название товара
    SUM(ds.dr_kol) AS amount,                        -- количество штук
    SUM(ds.dr_croz - ds.dr_sdisc) AS profit_with_discount,  -- выручка со скидками
    SUM(ds.dr_kol) / COUNT(DISTINCT dr_dat) * 30 AS month_average  -- среднемесячное кол-во
  FROM 
    drugs_simulative ds 
  WHERE 
    ds.dr_ndrugs != ''
  GROUP BY 
    dr_ndrugs 
)
```

**Что происходит:**
- Группируем по каждому товару
- Суммируем три метрики
- Исключаем пустые названия товаров

---

### Шаг 2: Рассчитываем накопительную сумму (кумулятив)

```sql
, cumsum_table AS (
  SELECT 
    dr_ndrugs,
    -- Кумулятивный процент по КОЛИЧЕСТВУ (отсортировано по убыванию)
    ROUND(
      SUM(amount) OVER (ORDER BY amount DESC) / 
      SUM(amount) OVER () * 100.0, 
      2
    ) AS cumsum_count,
    
    -- Кумулятивный процент по ВЫРУЧКЕ
    ROUND(
      SUM(profit_with_discount) OVER (ORDER BY profit_with_discount DESC) / 
      SUM(profit_with_discount) OVER () * 100.0, 
      2
    ) AS cumsum_profit_with_disc,
    
    -- Кумулятивный процент по ОБОРАЧИВАЕМОСТИ
    ROUND(
      SUM(month_average) OVER (ORDER BY month_average DESC) / 
      SUM(month_average) OVER () * 100.0, 
      2
    ) AS cumsum_month_average
  FROM 
    group_table
)
```

**Что здесь:**
- `SUM(amount) OVER (ORDER BY amount DESC)` — нарастающая сумма по убыванию
- `SUM(amount) OVER ()` — общая сумма по всем товарам
- Делим на 100 → получаем **кумулятивный процент**
- Сортировка важна! Сначала берём товары с наибольшим объёмом

**Пример:**
```
Товар A: 100 единиц → 100/500 * 100 = 20% → кумулятив 20%
Товар B: 150 единиц → 150/500 * 100 = 30% → кумулятив 50%
Товар C: 140 единиц → 140/500 * 100 = 28% → кумулятив 78%
Товар D: 70 единиц → 70/500 * 100 = 14% → кумулятив 92%
Товар E: 40 единиц → 40/500 * 100 = 8% → кумулятив 100%
```

---

### Шаг 3: Классифицируем товары (A, B, C)

```sql
SELECT
  dr_ndrugs,
  
  -- ABC по КОЛИЧЕСТВУ
  CASE
    WHEN SUM(amount) OVER (ORDER BY amount DESC) / SUM(amount) OVER () * 100.0 <= 80 THEN 'A'
    WHEN SUM(amount) OVER (ORDER BY amount DESC) / SUM(amount) OVER () * 100.0 <= 95 THEN 'B'
    ELSE 'C'
  END AS ABC_count,
  
  -- ABC по ВЫРУЧКЕ
  CASE
    WHEN SUM(profit_with_discount) OVER (ORDER BY profit_with_discount DESC) / SUM(profit_with_discount) OVER () * 100.0 <= 80 THEN 'A'
    WHEN SUM(profit_with_discount) OVER (ORDER BY profit_with_discount DESC) / SUM(profit_with_discount) OVER () * 100.0 <= 95 THEN 'B'
    ELSE 'C'
  END AS ABC_profit_with_disc,
  
  -- ABC по ОБОРАЧИВАЕМОСТИ
  CASE
    WHEN SUM(month_average) OVER (ORDER BY month_average DESC) / SUM(month_average) OVER () * 100.0 <= 80 THEN 'A'
    WHEN SUM(month_average) OVER (ORDER BY month_average DESC) / SUM(month_average) OVER () * 100.0 <= 95 THEN 'B'
    ELSE 'C'
  END AS ABC_month_average,
  
  -- Комбинированная классификация
  ABC_count || ABC_profit_with_disc || ABC_month_average AS classification
FROM
  cumsum_table 
ORDER BY
  ABC_profit_with_disc DESC,
  ABC_count DESC,
  ABC_month_average DESC;
```

**Логика классификации:**
- ≤ 80% кумулятива → **A** (накопили основную часть)
- ≤ 95% кумулятива → **B** (накопили ещё часть)
- > 95% кумулятива → **C** (остаток)

---

## Полный SQL запрос

```sql
WITH group_table AS (
  SELECT
    ds.dr_ndrugs,
    SUM(ds.dr_kol) AS amount,
    SUM(ds.dr_croz - ds.dr_sdisc) AS profit_with_discount,
    SUM(ds.dr_kol) / COUNT(DISTINCT dr_dat) * 30 AS month_average  
  FROM 
    drugs_simulative ds 
  WHERE 
    ds.dr_ndrugs != ''
  GROUP BY 
    dr_ndrugs 
),
cumsum_table AS (
  SELECT 
    dr_ndrugs,
    ROUND(
      SUM(amount) OVER (ORDER BY amount DESC) / SUM(amount) OVER () * 100.0, 
      2
    ) AS cumsum_count,
    ROUND(
      SUM(profit_with_discount) OVER (ORDER BY profit_with_discount DESC) / 
      SUM(profit_with_discount) OVER () * 100.0, 
      2
    ) AS cumsum_profit_with_disc,
    ROUND(
      SUM(month_average) OVER (ORDER BY month_average DESC) / 
      SUM(month_average) OVER () * 100.0, 
      2
    ) AS cumsum_month_average,
    CASE
      WHEN SUM(amount) OVER (ORDER BY amount DESC) / SUM(amount) OVER () * 100.0 <= 80 THEN 'A'
      WHEN SUM(amount) OVER (ORDER BY amount DESC) / SUM(amount) OVER () * 100.0 <= 95 THEN 'B'
      ELSE 'C'
    END AS ABC_count,
    CASE
      WHEN SUM(profit_with_discount) OVER (ORDER BY profit_with_discount DESC) / 
           SUM(profit_with_discount) OVER () * 100.0 <= 80 THEN 'A'
      WHEN SUM(profit_with_discount) OVER (ORDER BY profit_with_discount DESC) / 
           SUM(profit_with_discount) OVER () * 100.0 <= 95 THEN 'B'
      ELSE 'C'
    END AS ABC_profit_with_disc,
    CASE
      WHEN SUM(month_average) OVER (ORDER BY month_average DESC) / 
           SUM(month_average) OVER () * 100.0 <= 80 THEN 'A'
      WHEN SUM(month_average) OVER (ORDER BY month_average DESC) / 
           SUM(month_average) OVER () * 100.0 <= 95 THEN 'B'
      ELSE 'C'
    END AS ABC_month_average
  FROM 
    group_table
)
SELECT
  dr_ndrugs,
  ABC_count || ABC_profit_with_disc || ABC_month_average AS classification,
  cumsum_count,
  cumsum_profit_with_disc,
  cumsum_month_average
FROM
  cumsum_table 
ORDER BY
  ABC_profit_with_disc,
  ABC_count,
  ABC_month_average;
```

---

## Интерпретация результатов

### Пример результата:
```
Товар              | Классификация | Что означает
Парацетамол        | AAA           | Топ по всем метрикам → максимальный приоритет
Ибупрофен          | AAB           | Топ по количеству и выручке, но медленнее оборачивается
Валидол            | CCB           | Низкий спрос, но занимает ценную полку
```

### Действия по категориям:

| Категория | Действие |
|-----------|----------|
| **AAA, AAB, ABA, ABB** | ✅ Всегда держать в наличии, высокий приоритет заказов |
| **BAA, BAB, BBA** | ⚠️ Поддерживать на среднем уровне, периодически проверять спрос |
| **CCC, CCB, CBC** | ❌ Рассмотреть снятие с ассортимента или переместить на менее ценное место |

---

## Ключевые выводы

1. **ABC анализ** — это не одна метрика, а несколько одновременно
2. **Закон Парето** помогает сосредоточиться на 20%, которые дают 80% результата
3. **Window функции** (`SUM() OVER`) — инструмент для расчёта кумулятива и классификации
4. **CTE (WITH)** — удобный способ разбить сложный запрос на части
5. **Многомерный анализ** даёт более полную картину, чем одномерный

---

## Практический совет

Используй ABC анализ для:
- Оптимизации ассортимента (убрать неходовое)
- Планирования закупок (A-товары закупаем чаще)
- Организации склада (A-товары на видных местах)
- Управления бюджетом рекламы (вложить в A-товары)
