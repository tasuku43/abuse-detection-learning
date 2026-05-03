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
evaluation_targets as (
    select
        user_id,
        datetime(label_time, '-30 minutes') as as_of_time,
        'human_label' as target_source
    from human_labels

    union all

    select
        app_users.user_id,
        datetime('2026-05-02 11:00:00', '-30 minutes') as as_of_time,
        'scheduled_unlabeled_sample' as target_source
    from app_users
    where not exists (
        select 1
        from human_labels
        where human_labels.user_id = app_users.user_id
    )
),
event_counts as (
    select
        evaluation_targets.user_id,
        evaluation_targets.as_of_time,
        sum(case when event_type = 'contact_created' then 1 else 0 end) as contacts_24h,
        sum(case when event_type = 'message_sent' and event_time >= datetime(evaluation_targets.as_of_time, '-1 hour') then 1 else 0 end) as messages_1h,
        sum(case when event_type = 'profile_updated' then 1 else 0 end) as profile_updates_24h,
        sum(case when event_type = 'new_device_login' then 1 else 0 end) as device_count_24h,
        sum(case when event_type = 'failed_login' then 1 else 0 end) as failed_login_count_24h,
        sum(case when event_type = 'country_changed' then 1 else 0 end) as login_country_changes_24h,
        sum(case when event_type = 'password_reset' then 1 else 0 end) as password_reset_24h,
        sum(case when event_type = 'recipient_blocked' then 1 else 0 end) as recipient_blocks_24h,
        sum(case when event_type = 'message_sent' then 1 else 0 end) as messages_24h,
        sum(case when event_type = 'message_sent' and event_time >= datetime(evaluation_targets.as_of_time, '-1 hour') and event_detail = 'link' then 1 else 0 end) as link_messages_1h
    from evaluation_targets
    left join warehouse_user_behavior_logs
        on warehouse_user_behavior_logs.user_id = evaluation_targets.user_id
       and warehouse_user_behavior_logs.event_time < evaluation_targets.as_of_time
       and warehouse_user_behavior_logs.event_time >= datetime(evaluation_targets.as_of_time, '-24 hours')
    group by
        evaluation_targets.user_id,
        evaluation_targets.as_of_time
),
status_snapshots_as_of as (
    select
        evaluation_targets.user_id,
        evaluation_targets.as_of_time,
        app_user_status_snapshots.account_status,
        app_user_status_snapshots.plan,
        app_user_status_snapshots.email_verified,
        app_user_status_snapshots.phone_verified,
        app_user_status_snapshots.profile_completeness,
        row_number() over (
            partition by evaluation_targets.user_id, evaluation_targets.as_of_time
            order by app_user_status_snapshots.snapshot_time desc
        ) as snapshot_rank
    from evaluation_targets
    join app_user_status_snapshots
        on app_user_status_snapshots.user_id = evaluation_targets.user_id
       and app_user_status_snapshots.snapshot_time <= evaluation_targets.as_of_time
)
select
    evaluation_targets.user_id,
    evaluation_targets.as_of_time,
    date(evaluation_targets.as_of_time) as partition_date,
    evaluation_targets.target_source,
    cast((julianday(evaluation_targets.as_of_time) - julianday(app_users.created_at)) * 24 * 60 as integer) as account_age_minutes,
    coalesce(event_counts.contacts_24h, 0) as contacts_24h,
    coalesce(event_counts.messages_1h, 0) as messages_1h,
    coalesce(event_counts.profile_updates_24h, 0)
        + case when app_user_profiles.profile_created_at < evaluation_targets.as_of_time then 1 else 0 end
        + case when app_user_profiles.avatar_uploaded_at is not null and app_user_profiles.avatar_uploaded_at < evaluation_targets.as_of_time then 1 else 0 end
        + case when status_snapshots_as_of.email_verified = 1 then 0 else 1 end
        + case when status_snapshots_as_of.phone_verified = 1 then 0 else 1 end
        + case when status_snapshots_as_of.profile_completeness < 50 then 1 else 0 end
        as profile_updates_24h,
    coalesce(event_counts.device_count_24h, 0) as device_count_24h,
    coalesce(event_counts.failed_login_count_24h, 0) as failed_login_count_24h,
    coalesce(event_counts.login_country_changes_24h, 0) as login_country_changes_24h,
    coalesce(event_counts.password_reset_24h, 0) as password_reset_24h,
    case
        when coalesce(event_counts.messages_24h, 0) = 0 then 0.0
        else round(cast(event_counts.recipient_blocks_24h as real) / event_counts.messages_24h, 4)
    end as recipient_block_rate_24h,
    case
        when coalesce(event_counts.messages_1h, 0) = 0 then 0.0
        else round(cast(event_counts.link_messages_1h as real) / event_counts.messages_1h, 4)
    end as message_link_ratio_1h,
    status_snapshots_as_of.plan,
    app_users.signup_method,
    app_users.initial_country,
    status_snapshots_as_of.account_status as account_status_as_of,
    status_snapshots_as_of.email_verified,
    status_snapshots_as_of.phone_verified,
    status_snapshots_as_of.profile_completeness,
    app_user_profiles.bio_length,
    case
        when app_user_profiles.avatar_uploaded_at is not null
         and app_user_profiles.avatar_uploaded_at < evaluation_targets.as_of_time then 1
        else 0
    end as avatar_uploaded
from evaluation_targets
join app_users
    on app_users.user_id = evaluation_targets.user_id
join app_user_profiles
    on app_user_profiles.user_id = evaluation_targets.user_id
join status_snapshots_as_of
    on status_snapshots_as_of.user_id = evaluation_targets.user_id
   and status_snapshots_as_of.as_of_time = evaluation_targets.as_of_time
   and status_snapshots_as_of.snapshot_rank = 1
left join event_counts
    on event_counts.user_id = evaluation_targets.user_id
   and event_counts.as_of_time = evaluation_targets.as_of_time
where status_snapshots_as_of.account_status = 'active'
order by evaluation_targets.user_id
