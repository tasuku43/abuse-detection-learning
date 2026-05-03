-- Learning skeleton only.
-- User behavior logs are user actions used to build behavior features.

select
    event_id,
    user_id,
    event_time,
    event_name,
    event_properties
from {{ source('learning_raw', 'user_behavior_logs') }}
