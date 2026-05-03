-- Learning skeleton only.
-- In a real warehouse, this model would standardize user account fields.

select
    user_id,
    created_at,
    plan
from {{ source('learning_raw', 'account_attributes') }}
