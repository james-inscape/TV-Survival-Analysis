--Pull a list of TVs that were activated > 1 year ago: TV_DoB > 12 months
--Determine a dead tv as one that has not been active in the past year. For this reason
--pull back the last session date to one year ago. Otherwise, there will be no TVs dying 
--in the later months: e.g. months_elapsed between 48 and 60 if these were the last 12 months
--We will only see brand activity from live tvs in the past year.
--The TV has to be born 2 years + ago

create table tv_survival8 as
(
with tvs as
(
select a.tvid, a.chipset, trunc(a.joined_date) as tv_dob,
en.curr_max_session_start, en.curr_min_session_start, en.tv_active, max(c.session_start) as prev_max_session_start 

from (select distinct fk_tvid, 
case when max(session_start) < current_date - 365 then 'No'
else 'Yes' end as tv_active,
max(session_start) as curr_max_session_start,
min(session_start) as curr_min_session_start
from detection.tv_activity
group by 1) en 

join detection.tv a on a.tvid = en.fk_tvid
join detection.tv_populations b on a.tvid = b.fk_tvid
join detection.tv_activity c on c.fk_tvid = a.tvid
where [tv_dob] < current_date - 730 and c.session_start < current_date - 365
group by 1,2,3,4,5,6
)

select 
tvid, tv_active, tv_dob, curr_max_session_start, curr_min_session_start, prev_max_session_start,
datediff(month,tv_dob,prev_max_session_start) as months_elapsed,

 sum(CASE WHEN lower(chipset) like '%sigma%' THEN 1 ELSE 0 END) as "sigma"
, sum(CASE WHEN lower(chipset) like '%mseries%' THEN 1 ELSE 0 END) as "mseries"
, sum(CASE WHEN lower(chipset) not like '%sigma%' and lower(chipset) not like '%mseries%' THEN 1 ELSE 0 END) as "other"

from tvs

group by 1, 2, 3, 4, 5, 6, 7);





--Validation Metrics
select * from tv_survival8 limit 100;
select count(tvid), count(distinct tvid) from tv_survival8;
select tv_active, count(tvid) from tv_survival8 group by 1;

select tv_active, 
min(curr_max_session_start) as curr_max_session_start, 
min(prev_max_session_start) as prev_max_session_start,
min(tv_dob)
from tv_survival8
group by 1;

select datepart('year', joined_date), count(*) from detection.tv
group by 1;

select tv_active, avg(months_elapsed) as mean_te, median(months_elapsed) as median_me from tv_survival8 group by 1;
