-- Teacher labels should come from human review outcomes.
-- Automated action outcomes are excluded so the evaluation does not learn from
-- the current detector's own decisions.

with operator_action_logs as (
    select * from {{ ref('stg_operator_action_logs') }}
),

human_actions as (
    select
        user_id,
        event_time as label_time,
        1 as label_value,
        reason_code
    from operator_action_logs
    where actor_type = 'human_operator'
      and action_name in ('suspend_user', 'confirm_account_takeover', 'confirm_spam_account')
)

select
    user_id,
    label_time,
    label_value,
    reason_code
from human_actions
