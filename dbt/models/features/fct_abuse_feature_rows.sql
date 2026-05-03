-- Point-in-time feature rows for offline evaluation.
-- Every event join uses event_time < as_of_time to avoid future information.

with targets as (
    select * from {{ ref('evaluation_targets') }}
),

account_attributes as (
    select * from {{ ref('stg_account_attributes') }}
),

user_behavior_logs as (
    select * from {{ ref('stg_user_behavior_logs') }}
),

feature_rows as (
    select
        targets.user_id,
        targets.as_of_time,
        targets.label_value,
        datediff('minute', account_attributes.created_at, targets.as_of_time) as account_age_minutes,
        count_if(user_behavior_logs.event_name = 'contact_created'
            and user_behavior_logs.event_time >= targets.as_of_time - interval '24 hour') as contacts_24h,
        count_if(user_behavior_logs.event_name = 'message_sent'
            and user_behavior_logs.event_time >= targets.as_of_time - interval '1 hour') as messages_1h,
        count_if(user_behavior_logs.event_name = 'profile_updated'
            and user_behavior_logs.event_time >= targets.as_of_time - interval '24 hour') as profile_updates_24h,
        count(distinct case
            when user_behavior_logs.event_name = 'login'
             and user_behavior_logs.event_time >= targets.as_of_time - interval '24 hour'
            then user_behavior_logs.event_properties:device_id
        end) as device_count_24h,
        count_if(user_behavior_logs.event_name = 'failed_login'
            and user_behavior_logs.event_time >= targets.as_of_time - interval '24 hour') as failed_login_count_24h,
        count(distinct case
            when user_behavior_logs.event_name = 'login'
             and user_behavior_logs.event_time >= targets.as_of_time - interval '24 hour'
            then user_behavior_logs.event_properties:country_code
        end) as login_country_changes_24h,
        max(case
            when user_behavior_logs.event_name = 'password_reset'
             and user_behavior_logs.event_time >= targets.as_of_time - interval '24 hour'
            then 1 else 0
        end) as password_reset_24h,
        coalesce(
            count_if(user_behavior_logs.event_name = 'recipient_blocked'
                and user_behavior_logs.event_time >= targets.as_of_time - interval '24 hour')::float
            / nullif(count_if(user_behavior_logs.event_name = 'message_sent'
                and user_behavior_logs.event_time >= targets.as_of_time - interval '24 hour'), 0),
            0.0
        ) as recipient_block_rate_24h,
        coalesce(
            count_if(user_behavior_logs.event_name = 'message_sent_with_link'
                and user_behavior_logs.event_time >= targets.as_of_time - interval '1 hour')::float
            / nullif(count_if(user_behavior_logs.event_name = 'message_sent'
                and user_behavior_logs.event_time >= targets.as_of_time - interval '1 hour'), 0),
            0.0
        ) as message_link_ratio_1h,
        account_attributes.plan
    from targets
    join account_attributes
      on targets.user_id = account_attributes.user_id
    left join user_behavior_logs
      on targets.user_id = user_behavior_logs.user_id
     and user_behavior_logs.event_time < targets.as_of_time
    group by
        targets.user_id,
        targets.as_of_time,
        targets.label_value,
        account_attributes.created_at,
        account_attributes.plan
)

select * from feature_rows
