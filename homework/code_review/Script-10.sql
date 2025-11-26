-- + Нужно посчитать количество купленных задач и тестов (опираемся на таблицу Транзакций). 
-- + Интересно, сколько в сумме купили закрытые задачи и тесты (отдельно - задачи, отдельно - тесты),
 
-- а также в среднем на 1 пользователя платформы (даже если он вообще не проявлял никакой активности) - также отдельно по задачам и тестам. 
-- Также стоит посмотреть, сколько людей купили хотя бы 1 задачу/тест, а сколько решали только бесплатные. 
-- Дополнительно выведите, сколько людей вообще не решали ни одной задачи, а также не делали ни одной попытки пройти тест. 

-- Этой задачи уже нет в симуляторе - она была в старой версии, но мы ее убрали. 
--Поэтому вот небольшие пояснения перед задачей:
 
-- За покупку задач в таблице транзакций отвечает type_id 23, за покупку тестов - 27. 
-- Такие задачи считаются закрытыми, и не доступны до покупки. 

-- Все остальные задачи (хранящиеся в codesubmit, coderun и problem_to_company) - считаем открытыми.

-- В расчетах исключайте всегда пользователей с id < 94 - это наши внутренние аккаунты. 
-- При анализе задач также исключайте из расчета те задачи, 
-- которые присутствуют в problem_to_company и имеют отношение к компании пользователя, 
-- решавшего задачу - это домашние задания для студентов, они тоже искажают статистику.

--Например, если у пользователя 10 компания и он решает задачу с номером 300, 
-- а в таблице problem_to_company эта задача фигурирует как домашняя для компании 10 - ее нужно исключить. 

--Ответ можете сформировать в виде таблицы из 1 строки и 10 столбцов, 
--а можете организовать 2 строки (одна для тестов, другая - для задач) и сократить число столбцов до 5. 

select
	*
	, count(case when t.type_id = 23 then t.id end) over() as cnt_pay_task
	, count(case when t.type_id = 27 then t.id end) over() as cnt_pay_test
from
	"transaction" t 

	
	
--	         open   count_user  count_closed    avg_count_closed    count_user_open
-- problem	19605	514			1550			3.02				322
-- test		1444	671			953				1.42				526

	
with A as (
   --выводим расчеты по задачам
	select 
   		(select count(*) from codesubmit c  where c.user_id>=94) - count( t.id) as open , --кол-во открытых задач
       	count(distinct t.user_id) as count_user, --кол-во людей купивших хотя бы 1 задачу
       	count( t.id) as count_closed, --сумма купленных закрытых задач
       	round(count(t.id)*1.0/count(distinct t.user_id),2) as avg_count_closed, --среднее кол-во задач на пользователя
       	(select count(distinct c.user_id)
       	from codesubmit c
       	where c.user_id>=94
       	) - count(distinct t.user_id) as count_user_open --количество пользователей, решавших только бесплатные задачи
    from 
    	transaction t
	where 
		t.type_id =23 --покупка задач
		and t.user_id>=94
),
B as (
	--выводим расчеты по тестам
	select 
		(select count(*) from teststart t2  where t2.user_id>=94) - count( t.id) as open, --кол-во открытых тестов
       	count(distinct t.user_id) as count_user, --кол-во людей купивших хотя бы 1 тест
       	count( t.id) as count_closed, --сумма купленных закрытых тестов
       	round(count(t.id)*1.0/count(distinct t.user_id),2) as avg_count_closed, --среднее кол-во тестов на пользователя
       	(select count(distinct t2.user_id) from teststart t2 where t2.user_id >= 94) - count(distinct t.user_id) as count_user_open --количество пользователей, решавших только бесплатные тесты
	from 
		transaction t
	where 
		t.type_id =27 --покупка теста
		and t.user_id>=94)
--сводим результаты	 
select 'problem',*
from A
union
select 'test',*
from B





-- Сколько монет в среднем списывает пользователь за весь срок жизни? 
-- Сколько монет ему начисляется? 
-- Какая в среднем по пользователям разница между начислениями и списаниями?

-- Примечание: В расчетах “среднего” учитывайте только тех пользователей, у которых в целом были какие-то транзакции. 

-- В расчетах исключайте всегда пользователей с id < 94 - это наши внутренние аккаунты. 
-- Когда будете работать с таблицей Транзакций, 
-- не берите в расчет транзакции больше или равные 500 монетам - это начисления бета-тестерам, они будут сильно мешать.



with agg_sum as (
  select 
    t.user_id
    , sum(case when t.type_id in(2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,29) then t.value else 0 end) as sum_accruals -- начисления    
    , sum(case when t.type_id in(1,23,24,25,26,27,28) then t.value else 0 end) as sum_write_off -- списания 
  from transaction t
  where 
     t.value < 500 and t.user_id >= 94
  group by 
    t.user_id
), -- посдчет начислений и списаний с помощью агрегации
agg_avg as (
  select
    avg(sum_write_off) as avg_write_off
    , avg(sum_accruals) as avg_accruals 
    , avg(sum_accruals - sum_write_off) as delta
  from
    agg_sum
) -- подсчет среднего по начислениям и списаниям
select
  round(avg_write_off, 2) as avg_write_off
  , round(avg_accruals, 2) as avg_accruals 
  , round(delta, 2)  as delta
from
  agg_avg

  
  -- 29.14	119.27	90.13

  
with A as (select sum(t.value) as sum_value,  
                t.user_id                 
               from transaction t
               where t.type_id in(2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,29) --id начислений
               and t.value<=500
               and t.user_id>=94
               group by t.user_id
          ), --начисление по каждому юзеру
   A1 as (select round (sum(A.sum_value)/count(A.user_id), 2) as среднее_начисление
          from A), /*вывод среднего начисления */  
   B as (select round(sum(t.value)*1.0/count(A.user_id ), 2) as среднее_списание
               from A
               left join transaction t on t.user_id =A.user_id
               where t.type_id in(1,23,24,25,26,27,28) --id списаний
               and t.value<=500
               and t.user_id>=94
         ) /*вывод среднего списания */         
        select A1.среднее_начисление,
               B.среднее_списание,
               A1.среднее_начисление-B.среднее_списание as дельта
        from A1, B




        
        
-- 1. выровнить отступы , пробелы, переносы строки, для лучшей читаемости и опрятности. 
-- 2. сделать осмысленные названия столбцов и переменных.
-- 3. сократить количество временных таблиц с помощью решения case (сумму списания и сумму начислений можно воспроизвести в одной CTE)
-- 4. убрать лишние join
-- 5. правильно посчитать среднее
-- 6. фильтр t.value <= 500 не корректен, в задании "не берите в расчет транзакции больше или равные 500 монетам"
-- 7. вывести ответ в последовательности постановки вопросов, а именно:
    -- Сколько монет в среднем списывает пользователь за весь срок жизни? 
    -- Сколько монет ему начисляется? 
    -- Какая в среднем по пользователям разница между начислениями и списаниями?


✔ Код полностью соответствует бизнес-требованиям
✔ Учитывает только пользователей с транзакциями
✔ Исключает внутренние аккаунты
✔ Исключает транзакции ≥ 500
✔ Правильно считает суммы начислений и списаний
✔ Правильно считает средние значения
✔ Правильно считает «среднюю разницу по пользователям»
✔ Структура чистая, читаемая
✔ Нет лишних JOIN
✔ Нет ошибок агрегации

-- -70.25	120.53	89.19


        
        
        
        
with accrual_table as (
	select
		user_id
		, sum(value) as accruals_avg_money
	from
		transaction tr
	where
		(type_id = 29 or type_id between 2 and 22) and value < 500
	group by
		user_id
),
write_of_table as (
	select
		user_id
		, sum(-value) as write_of_avg_money
	from
		transaction tr
	where
		(type_id = 1 or type_id between 23 and 28) and value < 500
	group by
		user_id
)
select
	round(avg(wt.write_of_avg_money ), 2) as write_of
	, round(avg(at.accruals_avg_money ), 2) as accruals
	, round(avg(coalesce(at.accruals_avg_money, 0) + coalesce(wt.write_of_avg_money, 0)), 2) as balance
from
	accrual_table at full join write_of_table wt on at.user_id = wt.user_id  ;         
        

with union_table as (
	select created_at::date as ymd, user_id
	from coderun where created_at::date >= '2022-01-01'
		union
	select created_at::date as ymd, user_id
	from codesubmit where created_at::date >= '2022-01-01'
)
select 
	min(ymd)
	, max(ymd)
from
	union_table





with union_table as (
	select created_at::date as ymd, user_id
	from coderun where created_at::date >= '2022-01-01'
		union
	select created_at::date as ymd, user_id
	from codesubmit where created_at::date >= '2022-01-01'
),
min_date as (
	select
		user_id
	    , min(ymd) over(partition by user_id) as first_entry 
	from
		union_table
	order by
		first_entry asc 
),
agg as (
	select
		first_entry
		, count(distinct user_id) as unique_users
	from
		min_date
	group by
		first_entry 
)
select
	dt as ymd 
	, sum(unique_users) over(order by dt asc) as unique_cnt
from 
	(select date_trunc('day', gen_dt)::date as dt
	from generate_series(
	        '2022-01-01'::timestamp,
	        (select max(ymd) from union_table)::timestamp,
	        '1 day'
	     ) as gen_dt) as gs left join agg on gs.dt = agg.first_entry 




with join_table as (
  select
    u.id as user_id
    , u.date_joined 
    , ue.entry_at
    , to_char(u.date_joined, 'YYYY-MM') as cohort 
  from 
    userentry ue join users u on ue.user_id = u.id 
  where
    extract(year from u.date_joined) = 2022
)
select
  cohort
  , round(count(case when entry_at::date - date_joined::date = 0 then 1 end) * 100.0 / count(case when entry_at::date - date_joined::date = 0 then 1 end), 2) as "0 (%)"
  , round(count(case when entry_at::date - date_joined::date = 1 then 1 end) * 100.0 / count(case when entry_at::date - date_joined::date = 0 then 1 end), 2) as "1 (%)"
  , round(count(case when entry_at::date - date_joined::date = 3 then 1 end) * 100.0 / count(case when entry_at::date - date_joined::date = 0 then 1 end), 2) as "3 (%)"
  , round(count(case when entry_at::date - date_joined::date = 7 then 1 end) * 100.0 / count(case when entry_at::date - date_joined::date = 0 then 1 end), 2) as "7 (%)"
  , round(count(case when entry_at::date - date_joined::date = 14 then 1 end) * 100.0 / count(case when entry_at::date - date_joined::date = 0 then 1 end), 2) as "14 (%)"
  , round(count(case when entry_at::date - date_joined::date = 30 then 1 end) * 100.0 / count(case when entry_at::date - date_joined::date = 0 then 1 end), 2) as "30 (%)"
  , round(count(case when entry_at::date - date_joined::date = 60 then 1 end) * 100.0 / count(case when entry_at::date - date_joined::date = 0 then 1 end), 2) as "60 (%)"
  , round(count(case when entry_at::date - date_joined::date = 90 then 1 end) * 100.0 / count(case when entry_at::date - date_joined::date = 0 then 1 end), 2) as "90 (%)"
from
  join_table
group by
  cohort;



with join_table as (
  select
    u.id as user_id,
    u.date_joined::date as date_joined,
    ue.entry_at::date as entry_at,
    (ue.entry_at::date - u.date_joined::date) as diff,
    to_char(u.date_joined, 'YYYY-MM') as cohort
  from userentry ue
  join users u on ue.user_id = u.id
  where extract(year from u.date_joined) = 2022
)
select
  cohort,
  round(count(distinct case when diff = 0  then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "0 (%)",
  round(count(distinct case when diff = 1  then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "1 (%)",
  round(count(distinct case when diff = 3  then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "3 (%)",
  round(count(distinct case when diff = 7  then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "7 (%)",
  round(count(distinct case when diff = 14 then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "14 (%)",
  round(count(distinct case when diff = 30 then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "30 (%)",
  round(count(distinct case when diff = 60 then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "60 (%)",
  round(count(distinct case when diff = 90 then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "90 (%)"
from join_table
group by cohort;



with join_table as (
  select
    u.id as user_id,
    date(ue.entry_at) as entry_at,
    date(u.date_joined) as date_joined,
    extract(day from ue.entry_at - u.date_joined) as diff,
    to_char(u.date_joined, 'YYYY-MM') as cohort
  from userentry ue
  join users u on ue.user_id = u.id
  where to_char(u.date_joined, 'YYYY') = '2022'
)
select
  cohort,
  round(count(distinct case when diff = 0  then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "0 (%)",
  round(count(distinct case when diff = 1  then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "1 (%)",
  round(count(distinct case when diff = 3  then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "3 (%)",
  round(count(distinct case when diff = 7  then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "7 (%)",
  round(count(distinct case when diff = 14 then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "14 (%)",
  round(count(distinct case when diff = 30 then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "30 (%)",
  round(count(distinct case when diff = 60 then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "60 (%)",
  round(count(distinct case when diff = 90 then user_id end) * 100.0 /
        count(distinct case when diff = 0 then user_id end), 2) as "90 (%)"
from join_table
group by cohort;





with join_table as (
  select
    u.id as user_id,
    ue.entry_at::date as entry_at,
    u.date_joined::date as date_joined,
    (ue.entry_at::date - u.date_joined::date) as diff,
    to_char(u.date_joined, 'YYYY-MM') as cohort
  from userentry ue
  join users u on ue.user_id = u.id
  where extract(year from u.date_joined) = 2022
)
select
  cohort,
  round(count(case when diff = 0  then user_id end) * 100.0 /
        count(case when diff = 0 then user_id end), 2) as "0 (%)",
  round(count(case when diff = 1  then user_id end) * 100.0 /
        count(case when diff = 0 then user_id end), 2) as "1 (%)",
  round(count(case when diff = 3  then user_id end) * 100.0 /
        count(case when diff = 0 then user_id end), 2) as "3 (%)",
  round(count(case when diff = 7  then user_id end) * 100.0 /
        count(case when diff = 0 then user_id end), 2) as "7 (%)",
  round(count(case when diff = 14 then user_id end) * 100.0 /
        count(case when diff = 0 then user_id end), 2) as "14 (%)",
  round(count(case when diff = 30 then user_id end) * 100.0 /
        count(case when diff = 0 then user_id end), 2) as "30 (%)",
  round(count(case when diff = 60 then user_id end) * 100.0 /
        count(case when diff = 0 then user_id end), 2) as "60 (%)",
  round(count(case when diff = 90 then user_id end) * 100.0 /
        count(case when diff = 0 then user_id end), 2) as "90 (%)"
from join_table
group by cohort;



select
	--*
	distinct to_char(ue.entry_at, 'YYYY-MM')
from
	userentry ue
where
	to_char(ue.entry_at, 'YYYY-MM') in (with agg as (
														select
															to_char(ue.entry_at, 'YYYY-MM') as year_month 
															, count(distinct ue.entry_at::date) as cnt_dt
														from
															userentry ue 
														group by
															to_char(ue.entry_at, 'YYYY-MM')
														having 
															count(distinct ue.entry_at::date) >= 25 
														order by 
															to_char(ue.entry_at, 'YYYY-MM')
													)
													select
														year_month
													from
														agg
																							)

																							
																							
																																													
--2021-11	30
--2021-12	31
--2022-01	31
--2022-02	28
--2022-03	30
--2022-04	30
																							
																							
																							

select
	to_char(ue.entry_at, 'YYYY-MM') as year_month 
	, count(distinct ue.entry_at::date) as cnt_dt
from
	userentry ue 
group by
	to_char(ue.entry_at, 'YYYY-MM')
having 
	count(distinct ue.entry_at::date) >= 25 
order by 
	to_char(ue.entry_at, 'YYYY-MM')
; 


with agg as (
	select
		to_char(ue.entry_at, 'YYYY-MM') as year_month 
		, count(distinct ue.entry_at::date) as cnt_dt
	from
		userentry ue 
	group by
		to_char(ue.entry_at, 'YYYY-MM')
	having 
		count(distinct ue.entry_at::date) >= 25 
	order by 
		to_char(ue.entry_at, 'YYYY-MM')
)
select
	year_month
from
	agg

;




select
	--*
--	to_char(ue.entry_at, 'YYYY-MM') as year_month 
--	, 
	distinct ue.entry_at::date
from
	userentry ue 
where
	to_char(ue.entry_at, 'YYYY-MM') = '2021-04'   --20
order by
	ue.entry_at::date asc;







with union_table as (
  select user_id , to_char(created_at, 'YYYY-MM-DD') as dt from coderun
  union 
  select user_id , to_char(created_at, 'YYYY-MM-DD') as dt from codesubmit
  union
  select user_id , to_char(created_at, 'YYYY-MM-DD') as dt from teststart
),
agg as (
  select
    count(case when ut.user_id is not null then 1 end) as input
    , count(case when ut.user_id is null then 1 end) as not_input
  from
    userentry ue left join union_table ut on to_char(ue.entry_at, 'YYYY-MM-DD') = ut.dt and ue.user_id = ut.user_id 
)
select
  round(sum(not_input) / (sum(input) + sum(not_input)) * 100, 2) as entries_without_activities
from
  agg;



with union_table as (
  select user_id , to_char(created_at, 'YYYY-MM-DD') as dt from coderun
  union 
  select user_id , to_char(created_at, 'YYYY-MM-DD') as dt from codesubmit
  union
  select user_id , to_char(created_at, 'YYYY-MM-DD') as dt from teststart
)
select
    round(sum(case when ut.user_id is null then 1 else 0 end) * 100.0 / count(*), 2) as entries_without_activities
  from
    userentry ue left join union_table ut on to_char(ue.entry_at, 'YYYY-MM-DD') = ut.dt and ue.user_id = ut.user_id 
;


with activities as (
    select
        user_id,
        to_char(created_at, 'YYYY-MM-DD') as dt
    from
        coderun c
    union
    select
        user_id,
        to_char(created_at, 'YYYY-MM-DD') as dt
    from
        codesubmit c2
    union
    select
        user_id,
        to_char(created_at, 'YYYY-MM-DD') as dt
    from
        teststart
)
select
    round(sum(case when a.user_id is null then 1 else 0 end)* 100.0 / count(*), 2) as entries_without_activities
from
    userentry u
left join activities a
on
    to_char(u.entry_at, 'YYYY-MM-DD') = a.dt
    and u.user_id = a.user_id;



-- 53.36
	

select
	distinct type_id
from
	transaction tr
order by
	type_id

select
	count(distinct user_id) as cnt_accruals
from
	transaction tr
where
	type_id = 29 or type_id between 2 and 22 and value < 500;	


select
	count(distinct user_id) as cnt_write_of
from
	transaction tr
where
	type_id = 1 or type_id between 23 and 28 and value < 500;

	
	
	
	
	
	
--where
--	type_id % 2 != 0




select
	(count(cr.id) + count(cs.id)) / count(distinct u.id ) as problems_avg 
	, count(ts.test_id) / count(distinct u.id )  as tests_avg
	, percentile_disc(0.5) within group(order by ts.test_id) as tests_median
from 
	users u 
right join
	teststart ts on u.id = ts.user_id 
join
	codesubmit cs on u.id = cs.user_id
join
	coderun cr on u.id = cr.user_id
	;


---


with problem_table as (
	select
		problem_id, user_id
	from
		codesubmit
	union all
	select
		problem_id, user_id
	from
		coderun
),
group_problem as (
	select
		user_id
		, count(distinct problem_id) as cnt_problems
	from
		problem_table pt join users u on pt.user_id = u.id 
	group by
		user_id
),
group_tests as (
	select
		ts.user_id
		, count(distinct ts.test_id ) as cnt_tests
	from
		teststart ts 
	group by
		ts.user_id
)
select
	round(avg(gp.cnt_problems ), 2) as problems_avg
	, round(avg(gt.cnt_tests ), 2) as tests_avg
	, percentile_disc(0.5) within group(order by gp.cnt_problems) as problems_median
	, percentile_disc(0.5) within group(order by gt.cnt_tests ) as tests_median
from 
	group_problem gp, group_tests gt ;





	

--	85.8423326133909287	21


with problem_table as (
	select
		id , user_id
	from
		codesubmit
	union all
	select
		id , user_id
	from
		coderun
)
select
	count(id)
from
	problem_table;







select
	count(cr.id)
from
	users u join coderun cr on u.id = cr.user_id;



select
	count(id) as cnt
from
	users;


select
	count(id) as cnt
from
	coderun; 
 

select
	count(id) as cnt
from
	codesubmit;

select
	count(id) as cnt
from
	teststart;


-- 79490 + 2582 = 82072




select
    user_id,
    sum(case when is_false = 1 then 1 else 0 end) as cnt
from codesubmit c
group by 
	user_id
order by
	user_id ASC;


select 
	cs.user_id 
	, count(is_false) as cnt
from
	codesubmit cs
where
	is_false = 1
group by
	cs.user_id
order by
	cs.user_id


select
	distinct u.username
	, u.email
from
	users as u
join 
	codesubmit as cs on u.id = cs.user_id 
left join
	testresult as tr on u.id = tr.user_id 
where
	u.company_id = 1 and tr.id is null;




select
	us.username 
	, us.email
	, to_char(us.date_joined , 'YYYY-MM-DD') as date_joined
from
	users as us 
where 
	us.id not in (select cs.user_id from codesubmit as cs)
	and
	us.company_id = 1;



select 
	u.username
	, u.email
	, to_char(u.date_joined , 'YYYY-MM-DD') as date_joined
from
	users as u 
left join 
	codesubmit as cs on u.id = cs.user_id 
where
	u.company_id = 1 and cs.id is null;


select count(*) from codesubmit where user_id is null;


select
	*
from
	codesubmit cs 
where
	cs.id is null








select
	u.username 
	, u.email 
	, t.name
	, tq.value as tq_value
	, ta.value as ta_value
	, ta.is_correct 
from 
	testresult tr 
join
	users u on tr.user_id = u.id 
join
	test t on tr.test_id = t.id 
join
	testquestion tq on tr.question_id = tq.id
left join
	testanswer ta on tr.answer_id = ta.id 
where
	u.company_id = 1;

select 
	*
from
	testanswer t  
where 
	id is not null


select
	*
from problem_to_company;

select
	*
from coderun c ;


