-- Evaluation targets define the user_id + as_of_time rows to score.
-- The label is attached after the target time so features can be computed
-- only from information available before as_of_time.

with account_attributes as (
    select * from {{ ref('stg_account_attributes') }}
),

human_labels as (
    select * from {{ ref('label_events_human') }}
),

positive_targets as (
    select
        user_id,
        label_time as as_of_time,
        1 as label_value
    from human_labels
),

negative_targets as (
    select
        user_id,
        created_at + interval '7 day' as as_of_time,
        0 as label_value
    from account_attributes
    where user_id not in (select user_id from human_labels)
)

select * from positive_targets
union all
select * from negative_targets
