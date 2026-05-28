# Модуль: HR Screening

---

# 0.1 Что такое JOIN и какие бывают?

JOIN — объединение таблиц по условию.

## Типы JOIN

### `INNER JOIN`

Возвращает только совпавшие строки.

### `LEFT JOIN`

Возвращает:

- все строки из левой таблицы,

- совпавшие строки из правой таблицы.

Если совпадений нет — значения справа будут `NULL`.

### `RIGHT JOIN`

Возвращает:

- все строки из правой таблицы,

- совпавшие строки из левой таблицы.

### `FULL OUTER JOIN`

Возвращает:

- совпавшие строки,

- несовпавшие строки из обеих таблиц.

### `CROSS JOIN`

Декартово произведение:

каждая строка первой таблицы соединяется с каждой строкой второй.

### `SELF JOIN`

JOIN таблицы самой с собой.

---

# 0.2.1 Чем отличаются COUNT(1), COUNT(*) и COUNT(column)?

## `COUNT(*)`

Считает количество всех строк результата запроса.

## `COUNT(1)`

Тоже считает количество всех строк.

`1` — просто константа.

Современные СУБД оптимизируют `COUNT(1)` и `COUNT(*)` одинаково.

## `COUNT(column)`

Считает только строки, где:

```sql

column IS NOT NULL

```

---

# 0.2.2 Чем отличаются SELECT(1), SELECT(*) и SELECT(column)?

## `SELECT *`

Возвращает все столбцы.

## `SELECT column`

Возвращает указанный столбец.

## `SELECT 1`

Возвращает константу `1` для каждой строки.

Часто используется внутри `EXISTS`, когда важен сам факт существования строки.

Пример:

```sql

SELECT *

FROM orders o

WHERE EXISTS (

    SELECT 1

    FROM users u

    WHERE u.id = o.user_id

);

```

---

# 0.3 В чем разница между CROSS JOIN и INNER JOIN?

## `INNER JOIN`

Объединяет таблицы по условию:

```sql

ON

```

Возвращает только совпавшие строки.

## `CROSS JOIN`

Создает декартово произведение.

Если:

- A = 10 строк,

- B = 100 строк,

то результат:

```text

10 * 100 = 1000 строк

```

`ON` не используется.

---

# 0.4 Когда используется FULL OUTER JOIN?

Когда нужно получить:

- совпавшие строки,

- строки только из левой таблицы,

- строки только из правой таблицы.

Используется для:

- поиска расхождений,

- сверки данных,

- аудита.

---

# 0.5 Результаты JOIN для двух таблиц (10 и 100 строк)

Пусть:

- A = 10 строк,

- B = 100 строк.

---

# 0.5.1 INNER JOIN

## Минимальное количество строк

```text

0

```

Если совпадений нет.

## Максимальное количество строк

Теоретически:

```text

10 * 100 = 1000

```

Если условие JOIN истинно для всех комбинаций строк.

На практике результат зависит от условия JOIN и ключей.

---

# 0.5.2 LEFT JOIN

## Минимальное количество строк

```text

10

```

Все строки левой таблицы сохраняются.

## Максимальное количество строк

Теоретически:

```text

1000

```

---

# 0.5.3 CROSS JOIN

## Количество строк

Всегда:

```text

10 * 100 = 1000

```

---

# 0.6 Чем отличаются UNION и UNION ALL?

## `UNION`

- объединяет результаты,

- удаляет дубликаты.

## `UNION ALL`

- объединяет результаты,

- НЕ удаляет дубликаты,

- работает быстрее.

---

# 0.7 В каком порядке выполняются SQL-операции?

Логический порядок выполнения:

```text

1. FROM + JOIN + ON

2. WHERE

3. GROUP BY

4. HAVING

5. SELECT

6. DISTINCT

7. ORDER BY

8. LIMIT / OFFSET

```

---

# 0.8 В чем отличие DELETE, TRUNCATE и DROP?

## `DELETE`

- удаляет строки,

- можно использовать `WHERE`,

- можно откатить,

- логируется построчно.

Пример:

```sql

DELETE FROM users

WHERE age < 18;

```

---

## `TRUNCATE`

- быстро удаляет все строки,

- без `WHERE`,

- обычно сбрасывает identity / auto increment.

Пример:

```sql

TRUNCATE TABLE users;

```

---

## `DROP`

Удаляет:

- таблицу,

- структуру,

- данные,

- индексы.

Пример:

```sql

DROP TABLE users;

```

---

# 0.9 В чем отличие WHERE и HAVING?

## `WHERE`

Фильтрует строки ДО агрегации.

## `HAVING`

Фильтрует результат ПОСЛЕ:

```sql

GROUP BY

```

## Неправильно

```sql

SELECT department, AVG(salary)

FROM employees

WHERE AVG(salary) > 50000

GROUP BY department;

```

## Правильно

```sql

SELECT department, AVG(salary)

FROM employees

GROUP BY department

HAVING AVG(salary) > 50000;

```

---

# 0.10 Какие типы оконных функций вы знаете?

## Ranking functions

### `ROW_NUMBER()`

Уникальный номер строки.

### `RANK()`

Ранг с пропусками.

### `DENSE_RANK()`

Ранг без пропусков.

### `NTILE()`

Разбиение на группы.

### `PERCENT_RANK()`

Процентный ранг.

### `CUME_DIST()`

Накопительное распределение.

---

## Aggregate window functions

### `SUM() OVER()`

### `AVG() OVER()`

### `COUNT() OVER()`

Агрегация без схлопывания строк.

---

## Value functions

### `LAG()`

Предыдущее значение.

### `LEAD()`

Следующее значение.

### `FIRST_VALUE()`

Первое значение окна.

### `LAST_VALUE()`

Последнее значение окна.

---

# 0.11 Какие типы агрегатных функций вы знаете?

## Основные агрегатные функции

### `COUNT()`

Количество строк.

### `SUM()`

Сумма.

### `AVG()`

Среднее значение.

### `MIN()`

Минимальное значение.

### `MAX()`

Максимальное значение.

---

## Дополнительные агрегатные функции

### `STRING_AGG()`

Объединение строк.

### `ARRAY_AGG()`

Сбор значений в массив.

### `BOOL_AND()`

TRUE, если все TRUE.

### `BOOL_OR()`

TRUE, если хотя бы одно TRUE.


# SQL Конспект

## 0. Порядок выполнения SQL-запророса (важно!)

**Визуально запрос написан так:**
```sql
SELECT col1, col2, agg_func(col3)
FROM table1
JOIN table2 ON condition
WHERE filter_condition
GROUP BY col1, col2
HAVING group_filter
ORDER BY col1
LIMIT n;
```

**А БД выполняет его в другом порядке (логический порядок):**

| Шаг | Ключевое слово | Что происходит |
|-----|----------------|----------------|
| 1 | `FROM` / `JOIN` | Определяем источник данных, строим декартово произведение, джойним |
| 2 | `WHERE` | **Фильтруем строки** (ещё без агрегатов) |
| 3 | `GROUP BY` | Группируем строки |
| 4 | `HAVING` | Фильтруем группы (после агрегации) |
| 5 | `SELECT` | Вычисляем выражения, агрегаты, псевдонимы |
| 6 | `ORDER BY` | Сортируем результат |
| 7 | `LIMIT` / `OFFSET` | Ограничиваем количество строк |

**Почему это важно знать:**

- `WHERE` **не может** использовать псевдонимы из `SELECT` (потому что `SELECT` выполняется позже)
  ```sql
  SELECT price * quantity AS total
  FROM orders
  WHERE total > 100;  -- ❌ ошибка! total ещё не существует
  ```

- `HAVING` может использовать агрегаты и псевдонимы
  ```sql
  SELECT category, SUM(price) AS total_sum
  FROM products
  GROUP BY category
  HAVING total_sum > 1000;  -- ✅ работает
  ```

- `WHERE` фильтрует **до** группировки, `HAVING` — **после**
  - `WHERE` быстрее → убирай лишнее до агрегации

- `ORDER BY` выполняется почти в самом конце, поэтому сортировка больших данных — дорого

---

## 1. Базовые команды (CRUD)

> **CRUD** — акроним из первых букв четырёх основных операций с данными:
> - **C**reate (создание) — `INSERT`
> - **R**ead (чтение) — `SELECT`
> - **U**pdate (обновление) — `UPDATE`
> - **D**elete (удаление) — `DELETE`

```sql
-- CREATE (вставка новых строк)
INSERT INTO users (name, email) VALUES ('John', 'john@mail.com');

-- READ (чтение данных)
SELECT * FROM users;

-- UPDATE (обновление существующих строк)
UPDATE users SET email = 'new@mail.com' WHERE id = 1;

-- DELETE (удаление строк)
DELETE FROM users WHERE id = 1;
```

**Фильтрация, сортировка, группировка**

```sql
SELECT category, COUNT(*), AVG(price)
FROM products
WHERE price > 100
GROUP BY category
HAVING COUNT(*) > 5
ORDER BY price DESC;
```

---

## 2. JOIN

```sql
-- INNER — только совпадения
SELECT * FROM orders o
INNER JOIN customers c ON o.customer_id = c.id;

-- LEFT — все из левой, NULL если нет в правой
SELECT * FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;

-- RIGHT — наоборот (редко)
-- FULL — все из обеих таблиц
```

---

## 3. UNION, INTERSECT, EXCEPT (работа с множествами)

Все три оператора работают с **двумя результатами запросов** (у них должно быть одинаковое количество и типы колонок).

### Визуальная разница (круги Эйлера)

```
    A          B
   ┌─┐        ┌─┐
   │1│      ┌─┤2├─┐
   │2├──────┤ │3│ │
   │3│      └─┤4├─┘
   └─┘        └─┘
```

| Оператор | Что делает | На примере |
|----------|-----------|------------|
| **UNION** | Всё из А и В (объединение) | {1,2,3,4} |
| **INTERSECT** | Только общее (пересечение) | {2,3} |
| **EXCEPT** | В А, но не в В (разность) | {1} |

---

### UNION — объединяет всё

```sql
SELECT name FROM employees
UNION                                    -- без дубликатов
SELECT name FROM managers;

-- UNION ALL — с дубликатами (быстрее)
SELECT name FROM employees
UNION ALL
SELECT name FROM managers;
```

**Запоминалка:** UNION = «объединение» → собираем **всё** из обоих.

---

### INTERSECT — только общее

```sql
SELECT name FROM employees
INTERSECT                                -- только те, кто и там, и там
SELECT name FROM managers;
```

**Запоминалка:** INTERSECT = «пересечение» → оставляем **только общее**.

---

### EXCEPT — чего нет во втором

```sql
SELECT name FROM employees
EXCEPT                                   -- сотрудники, которые НЕ менеджеры
SELECT name FROM managers;
```

**Запоминалка:** EXCEPT = «исключая» → берём из А **исключая** то, что есть в В.

---

### Важные правила

1. **Количество колонок** в обоих `SELECT` должно быть одинаковым
2. **Типы данных** колонок должны совместимы
3. **Порядок колонок** влияет на сравнение (сравнивается первая с первой, вторая со второй...)
4. `ORDER BY` пишется **в самом конце**, после последнего `SELECT`

```sql
(SELECT name FROM employees)
UNION
(SELECT name FROM managers)
ORDER BY name;   -- ORDER BY один на весь результат
```

## 4. CTE (Common Table Expression)

```sql
WITH high_orders AS (
    SELECT customer_id, SUM(amount) as total
    FROM orders
    GROUP BY customer_id
    HAVING SUM(amount) > 1000
)
SELECT c.name, h.total
FROM customers c
JOIN high_orders h ON c.id = h.customer_id;
```

---

## 5. CASE, COALESCE, NULLIF

```sql
-- CASE — условная логика
SELECT name,
    CASE 
        WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        ELSE 'C'
    END as grade
FROM students;

-- COALESCE — первый ненулевой
SELECT COALESCE(phone, mobile, 'no contact') FROM users;

-- NULLIF — NULL если равны (защита от деления на 0)
SELECT amount / NULLIF(quantity, 0) FROM sales;
```

---

## 6. EXISTS, ANY, ALL

```sql
-- EXISTS — есть хотя бы одна строка
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- ANY — больше любого (т.е. больше минимального)
SELECT * FROM products
WHERE price > ANY (SELECT price FROM products WHERE category = 'budget');

-- ALL — больше всех (т.е. больше максимального)
SELECT * FROM products
WHERE price > ALL (SELECT price FROM products WHERE category = 'budget');
```

---

## 7. Функции для работы со временем

```sql
-- EXTRACT — стандарт ANSI SQL, работает в большинстве БД
EXTRACT(YEAR FROM date_column)      -- год
EXTRACT(MONTH FROM date_column)     -- месяц (1-12)
EXTRACT(DAY FROM date_column)       -- день месяца
EXTRACT(HOUR FROM datetime_column)  -- час
EXTRACT(DOW FROM date_column)       -- день недели (0=воскресенье, 1=понедельник...)
EXTRACT(DOY FROM date_column)       -- день года (1-366)

-- Пример: все заказы за 2023 год
SELECT * FROM orders
WHERE EXTRACT(YEAR FROM order_date) = 2023;

-- Текущая дата - 7 дней
WHERE order_date >= CURRENT_DATE - INTERVAL '7 days';
```

---

## 8. Оптимизация SQL, индексы, партиции, витрины — практический гайд

> **Главная идея:** Не тащи всё в один запрос. Сначала сократи данные, потом считай.
>
> Тяжёлые вычисления делаем **редко и по расписанию**. Лёгкие чтения — **часто и из маленьких таблиц**.

### 8.1 Зачем оптимизировать

Плохой запрос = медленные дашборды + заблокированные задачи + счёт в облаке.

Хороший запрос = 2 минуты вместо 40 + ресурсы кластера свободны + экономия денег.

### 8.2 Что происходит при запросе (упрощённо)

1. Чтение с диска (самый дорогой шаг)
2. Фильтрация (`WHERE`)
3. Джойны (`JOIN`)
4. Агрегация (`GROUP BY`)
5. Сортировка и выдача (`ORDER BY`, `LIMIT`)

### 8.3 Индексы — как книжный указатель

**Когда индекс помогает:**
- Точный поиск: `WHERE user_id = 42`
- Диапазон: `WHERE created_at >= '2026-01-01'`
- JOIN по ключу
- Сортировка по индексированной колонке

**Когда индекс бесполезен:**
- Функция на колонке: `WHERE DATE(created_at) = '2026-04-01'` → надо переписать как диапазон
- Низкая селективность (колонка `is_active` с true/false)
- `LIKE '%что-то'` с процентом в начале
- На запись (каждый индекс замедляет INSERT/UPDATE/DELETE)

**Типы индексов:**

| Тип | Где встречается | Когда |
|-----|-----------------|-------|
| B-tree | Postgres, MySQL, везде | Дефолт. Равенство, диапазоны |
| BRIN | Postgres, Greenplum | Огромные таблицы с датами |
| GIN | Postgres | JSONB, массивы, полнотекстовый поиск |

**Составные индексы:**
Если индекс по `(user_id, created_at)`:
- ✅ работает: `WHERE user_id = 42`
- ✅ работает: `WHERE user_id = 42 AND created_at >= '2026-01-01'`
- ❌ не работает: `WHERE created_at >= '2026-01-01'` (без user_id)

### 8.4 Партиции — разрезаем таблицу на куски

**Когда спасают:**
- Таблица большая (десятки/сотни ГБ)
- В запросах почти всегда фильтр по дате
- Нужно быстро удалять старые данные (`DROP PARTITION`)

**Когда мешают:**
- Запрос без фильтра по ключу партиции → читает всё
- Слишком мелкое дробление (партиция на каждый день)

**Правило:** партиционируй по дате, по которой чаще всего фильтруешь. Гранулярность — месяц.

### 8.5 Типы сканов (что увидишь в EXPLAIN)

| Скан | Что делает | Когда |
|------|-----------|-------|
| Seq Scan | Читает всю таблицу | Нет индекса |
| Index Scan | Идёт по индексу → в таблицу | Есть индекс, селективность высокая |
| Index Only Scan | Всё берёт из индекса | Все нужные колонки в индексе |

### 8.6 Главный принцип: не тащи всё в один запрос

**❌ Плохо:** один гигантский запрос на 200 строк

**✅ Хорошо:** разнести по слоям

**Слой 1. Отфильтрованный срез**
```sql
CREATE TABLE stg_payments_q1_2026 AS
SELECT user_id, payment_id, amount
FROM raw_events
WHERE event_type = 'payment'
  AND created_at >= '2026-01-01'
  AND created_at < '2026-04-01';
```

**Слой 2. Агрегат (витрина)**
```sql
CREATE TABLE dm_dau AS
SELECT toDate(event_time) AS dt,
       COUNT(DISTINCT user_id) AS dau
FROM stg_events
GROUP BY dt;
```

**Слой 3. Витрина под конкретный дашборд** — уже посчитанные метрики в нужной гранулярности.

### 8.7 Практические приёмы (довести до автоматизма)

**1. Не клади функцию на индексированную колонку**
```sql
-- ❌ индекс по created_at не сработает
SELECT * FROM orders WHERE DATE(created_at) = '2026-04-01';

-- ✅
SELECT * FROM orders
WHERE created_at >= '2026-04-01'
  AND created_at < '2026-04-02';
```

**2. Не SELECT ***
```sql
-- ❌
SELECT * FROM users WHERE id = 42;

-- ✅
SELECT id, email FROM users WHERE id = 42;
```

**3. Фильтруй до JOIN, а не после**
```sql
-- ❌ сначала джойн, потом фильтр
SELECT * FROM orders o JOIN users u ON u.id = o.user_id
WHERE o.created_at >= '2026-01-01';

-- ✅ сначала фильтр, потом джойн
SELECT * FROM 
  (SELECT * FROM orders WHERE created_at >= '2026-01-01') o
JOIN users u ON u.id = o.user_id;
```

**4. Коррелированный подзапрос → JOIN с агрегацией**
```sql
-- ❌ подзапрос для каждой строки
SELECT u.id, (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS cnt
FROM users u;

-- ✅
SELECT u.id, COALESCE(o.cnt, 0) AS cnt
FROM users u
LEFT JOIN (SELECT user_id, COUNT(*) AS cnt FROM orders GROUP BY user_id) o
  ON o.user_id = u.id;
```

---

## Итог

Пишите не идеально оптимизированные запросы, а просто **адекватные**:
- фильтр по дате
- без `SELECT *`
- без коррелированных подзапросов
- тяжёлые вычисления — в витрину

Следуйте этим рекомендациям — получите + rep от коллег и лида.