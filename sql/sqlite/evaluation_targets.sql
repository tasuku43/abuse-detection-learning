with human_labels as (
    select
        user_id,
        action_time as label_time,
        case
            when action_type = 'human_suspend_abuse' then 1
            when action_type = 'human_review_clean' then 0
        end as label_value
    from warehouse_operator_action_logs
    where actor_type = 'human'
      and action_type in ('human_suspend_abuse', 'human_review_clean')
),
unlabeled_accounts as (
    select
        app_users.user_id,
        '2026-05-02 11:00:00' as label_time,
        0 as label_value
    from app_users
    where not exists (
        select 1
        from human_labels
        where human_labels.user_id = app_users.user_id
    )
)
select
    user_id,
    datetime(label_time, '-30 minutes') as as_of_time,
    'human_label' as target_source
from human_labels
union all
select
    user_id,
    datetime(label_time, '-30 minutes') as as_of_time,
    'scheduled_unlabeled_sample' as target_source
from unlabeled_accounts
