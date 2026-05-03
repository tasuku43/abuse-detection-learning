select
    eval_feature_rows.user_id,
    eval_feature_rows.as_of_time,
    eval_labels.label_value,
    eval_feature_rows.account_age_minutes,
    eval_feature_rows.contacts_24h,
    eval_feature_rows.messages_1h,
    eval_feature_rows.profile_updates_24h,
    eval_feature_rows.device_count_24h,
    eval_feature_rows.failed_login_count_24h,
    eval_feature_rows.login_country_changes_24h,
    eval_feature_rows.password_reset_24h,
    eval_feature_rows.recipient_block_rate_24h,
    eval_feature_rows.message_link_ratio_1h,
    eval_feature_rows.plan,
    eval_feature_rows.partition_date,
    eval_feature_rows.target_source,
    eval_feature_rows.signup_method,
    eval_feature_rows.initial_country,
    eval_feature_rows.account_status_as_of,
    eval_feature_rows.email_verified,
    eval_feature_rows.phone_verified,
    eval_feature_rows.profile_completeness,
    eval_feature_rows.bio_length,
    eval_feature_rows.avatar_uploaded
from eval_feature_rows
join eval_labels
    on eval_labels.user_id = eval_feature_rows.user_id
   and eval_labels.as_of_time = eval_feature_rows.as_of_time
order by eval_feature_rows.user_id
