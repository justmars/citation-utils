---
icon: lucide/database
---

# SQLite Analysis

Use normalized citation rows as an index and audit aid, not as a substitute for
the source document. Store the original text, document identifier, and source
location alongside `cat`, `num`, `date`, `phil`, `scra`, and `offg` whenever a
result may need legal review. The parser's `mentions` value counts recognized
source occurrences; it is not a measure of authority, treatment, or how often
a decision was cited across an entire corpus unless the query scope supplies
that meaning.

Assume citations have been collected into a database with the fields previously
established:

## Multiple category and serial having the same values

This state is valid but should result in connected decisions, e.g. a motion for reconsideration resolves an earlier decided case. This is the reason that a citation needs a `docket date` to distinguish connected cases.

Consider for instance the following query:

```sql
select
 docket_category, docket_serial, docket_date
from
 valid
where
 docket_category = "GR"
 and docket_serial = '109645'
order by docket_date desc
```

Yielding the connected _Ortigas_ decision rows which can be considered a collection of related cases:

1. ["GR","109645","2015-01-21"]
2. ["GR","109645","1997-08-15"]
3. ["GR","109645","1996-03-04"]
4. ["GR","109645","1994-07-25"]

Typographic errors in these category and serial pairings can result in an
unconnected case being considered part of an ostensible collection. The query
below is a review queue, not a finding of error: compare flagged rows to their
stored source evidence before correcting or merging them.

```sql
select
 count(docket_date) num,
 docket_category,
 docket_serial,
 min(docket_date) earliest,
 max(docket_date) latest,
 max(docket_date) - min(docket_date) diff, -- large difference is indicative of impropriety in at least one category / serial pair
 json_group_array(docket_date) dates,
 json_group_array(origin) origins,
 json_group_array(title) titles
from
 valid
where
 docket_date is not null
group by
 docket_category,
 docket_serial
having
 num >= 2
order by
 diff desc, num desc
```

## Inconsistent naming convention re: AM -SC

An Administrative Matter serial ending in `-SC` is not, by itself, a rule. The
extractor excludes only an explicit list of known statutory A.M. and B.M.
serials after canonicalization. Preserve the source and review a flagged row
before treating it as a statute or decision.

```sql
select
 title, docket_category, docket_serial, docket_date
from
 valid
where
 docket_category = "AM"
 and docket_serial like '%-sc'
order by docket_date desc
```

## Invalid citation patterns

```sql
-- present GRs: 68 rows
select * from main.invalid where orig_idx like '%g r%' or orig_idx like '%g.r%' or orig_idx like '%gr%'

-- admin matters: 50 rows
select * from main.invalid where orig_idx like '%a m%' or orig_idx like '%a.m%' or orig_idx like '%am%' or orig_idx like '%adm%m%'

-- admin cases: 113 rows
select * from main.invalid where orig_idx like '%a c%' or orig_idx like '%a.c%' or orig_idx like '%ac%' or orig_idx like '%adm%c%'

-- udks: 13 rows
select * from main.invalid where orig_idx like '%udk%'

-- PET cases: 7 rows
select * from main.invalid where orig_idx like '%p.e.t%'

-- too low char count: 65 rows
select * from main.invalid where length(orig_idx) <= 7
```

## Impropriety detector

```sql
SELECT
    COUNT(docket_date) num,
    docket_category,
    docket_serial,
    MIN(docket_date) earliest,
    MAX(docket_date) latest,
    MAX(docket_date) - MIN(docket_date) diff,
    -- large difference is indicative of impropriety in at least one category / serial pair
    json_group_array(docket_date) dates,
    json_group_array(origin) origins,
    json_group_array(title) titles
FROM
    valid
WHERE
    docket_date IS NOT NULL
GROUP BY
    docket_category,
    docket_serial
HAVING
    num >= 2
ORDER BY
    diff DESC,
    num DESC
```
