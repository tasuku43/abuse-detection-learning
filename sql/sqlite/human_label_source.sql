select
    user_id,
    action_time as label_time,
    datetime(action_time, '-30 minutes') as as_of_time,
    case
        when action_type = 'human_suspend_abuse' then 1
        when action_type = 'human_review_clean' then 0
    end as label_value
from warehouse_operator_action_logs
where actor_type = 'human'
  and action_type in ('human_suspend_abuse', 'human_review_clean')
