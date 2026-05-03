-- Learning skeleton only.
-- Operator action logs include human review outcomes and automated actions.

select
    event_id,
    user_id,
    event_time,
    actor_type,
    action_name,
    reason_code
from {{ source('learning_raw', 'operator_action_logs') }}
