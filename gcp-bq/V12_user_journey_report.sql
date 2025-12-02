WITH integration_events AS (
  SELECT
    user_pseudo_id,
    FORMAT_TIMESTAMP('%F %T', DATETIME(TIMESTAMP_MICROS(event_timestamp), "CET")) AS event_time,
    event_name,
    ROW_NUMBER() OVER (PARTITION BY user_pseudo_id ORDER BY event_timestamp) AS rn
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  WHERE
    event_name = 'integration_created_gmailemail' OR
    event_name = 'integration_created_outlookemail' OR
    event_name = 'integration_created_slack' OR
    event_name = 'integration_created_msteams' OR
    event_name = 'integration_created_googlecalendar' OR
    event_name = 'integration_created_outlookcalendar'
),

onboarding_user_ids AS (
  SELECT
    user_pseudo_id,
    user_id,
    ROW_NUMBER() OVER (PARTITION BY user_pseudo_id ORDER BY event_timestamp) AS rn
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  WHERE
    event_name = 'onboarding_step3_phone_verified_complete'
),

global_activity_days AS (
  SELECT
    user_pseudo_id,
    COUNT(DISTINCT DATE(TIMESTAMP_MICROS(event_timestamp))) AS total_active_days
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  WHERE
    event_name IS NOT NULL
  GROUP BY
    user_pseudo_id
),

aggregated_activity AS (
  SELECT
    user_pseudo_id,
    total_active_days,
    IF(total_active_days >= 2, TRUE, FALSE) AS step14_is_active_on_day_2,
    IF(total_active_days >= 5, TRUE, FALSE) AS step15_is_active_on_day_5,
    IF(total_active_days >= 10, TRUE, FALSE) AS step16_is_active_on_day_10
  FROM
    global_activity_days
),

last_30_days_activity AS (
  SELECT
    user_pseudo_id,
    COUNT(DISTINCT DATE(TIMESTAMP_MICROS(event_timestamp))) AS step17_days_active_in_last_30_days
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  WHERE
    event_name IS NOT NULL
    AND DATE(TIMESTAMP_MICROS(event_timestamp)) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY
    user_pseudo_id
),

message_events AS (
  SELECT
    user_pseudo_id,
    FORMAT_TIMESTAMP('%F %T', DATETIME(MIN(TIMESTAMP_MICROS(event_timestamp)), "CET")) AS step6_receives_and_opens_1st_message_or_email
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  WHERE
    event_name LIKE 'receive_3p_message_%'
    OR event_name LIKE 'receive_email_%'
    OR event_name = 'receive_statement_flags'
    OR event_name = 'receive_yesno_flags'
    OR event_name = 'receive_multichoice_flags'
    OR event_name = 'receive_location_share_flags'
    OR event_name = 'receive_location_request_flags'
    OR event_name = 'receive_eta_share_flags'
    OR event_name = 'receive_eta_request_flags'
    OR event_name = 'receive_status_share_flags'
    OR event_name = 'receive_status_request_flags'
    OR event_name LIKE 'open_3p_message_%'
    OR event_name LIKE 'open_email_%'
    OR event_name = 'open_statement_flags'
    OR event_name = 'open_yesno_flags'
    OR event_name = 'open_multichoice_flags'
    OR event_name = 'open_location_share_flags'
    OR event_name = 'open_location_request_flags'
    OR event_name = 'open_eta_share_flags'
    OR event_name = 'open_eta_request_flags'
    OR event_name = 'open_status_share_flags'
    OR event_name = 'open_status_request_flags'
  GROUP BY
    user_pseudo_id
),

message_events_10th AS (
  SELECT
    user_pseudo_id,
    FORMAT_TIMESTAMP('%F %T', DATETIME(TIMESTAMP_MICROS(event_timestamp), "CET")) AS step8_receives_and_opens_10th_msg_or_email
  FROM (
    SELECT
      user_pseudo_id,
      event_timestamp,
      ROW_NUMBER() OVER (PARTITION BY user_pseudo_id ORDER BY event_timestamp) AS rn
    FROM
      `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
    WHERE
      event_name LIKE 'receive_3p_message_%'
      OR event_name LIKE 'receive_email_%'
      OR event_name = 'receive_statement_flags'
      OR event_name = 'receive_yesno_flags'
      OR event_name = 'receive_multichoice_flags'
      OR event_name = 'receive_location_share_flags'
      OR event_name = 'receive_location_request_flags'
      OR event_name = 'receive_eta_share_flags'
      OR event_name = 'receive_eta_request_flags'
      OR event_name = 'receive_status_share_flags'
      OR event_name = 'receive_status_request_flags'
      OR event_name LIKE 'open_3p_message_%'
      OR event_name LIKE 'open_email_%'
      OR event_name = 'open_statement_flags'
      OR event_name = 'open_yesno_flags'
      OR event_name = 'open_multichoice_flags'
      OR event_name = 'open_location_share_flags'
      OR event_name = 'open_location_request_flags'
      OR event_name = 'open_eta_share_flags'
      OR event_name = 'open_eta_request_flags'
      OR event_name = 'open_status_share_flags'
      OR event_name = 'open_status_request_flags'
  )
  WHERE rn = 10
),

interaction_events AS (
  SELECT
    user_pseudo_id,
    FORMAT_TIMESTAMP('%F %T', DATETIME(MIN(TIMESTAMP_MICROS(event_timestamp)), "CET")) AS step7_sends_1st_email_or_message_or_status_share
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  WHERE
    event_name LIKE 'create_3p_message_%'
    OR event_name LIKE 'create_email_%'
    OR event_name = 'create_statement_flags'
    OR event_name = 'create_yesno_flags'
    OR event_name = 'create_multichoice_flags'
    OR event_name = 'create_location_share_flags'
    OR event_name = 'create_location_request_flags'
    OR event_name = 'create_eta_share_flags'
    OR event_name = 'create_eta_request_flags'
    OR event_name = 'create_status_share_flags'
    OR event_name = 'create_status_request_flags'
    OR event_name LIKE 'respond_3p_message_%'
    OR event_name LIKE 'respond_email_%'
    OR event_name = 'respond_statement_flags'
    OR event_name = 'respond_yesno_flags'
    OR event_name = 'respond_multichoice_flags'
    OR event_name = 'respond_location_share_flags'
    OR event_name = 'respond_location_request_flags'
    OR event_name = 'respond_eta_share_flags'
    OR event_name = 'respond_eta_request_flags'
    OR event_name = 'respond_status_share_flags'
    OR event_name = 'respond_status_request_flags'
  GROUP BY
    user_pseudo_id
),

interaction_events_5th AS (
  SELECT
    user_pseudo_id,
    FORMAT_TIMESTAMP('%F %T', DATETIME(TIMESTAMP_MICROS(event_timestamp), "CET")) AS step9_sends_5th_email_message_status_share
  FROM (
    SELECT
      user_pseudo_id,
      event_timestamp,
      ROW_NUMBER() OVER (PARTITION BY user_pseudo_id ORDER BY event_timestamp) AS rn
    FROM
      `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
    WHERE
      event_name LIKE 'create_3p_message_%'
      OR event_name LIKE 'create_email_%'
      OR event_name = 'create_statement_flags'
      OR event_name = 'create_yesno_flags'
      OR event_name = 'create_multichoice_flags'
      OR event_name = 'create_location_share_flags'
      OR event_name = 'create_location_request_flags'
      OR event_name = 'create_eta_share_flags'
      OR event_name = 'create_eta_request_flags'
      OR event_name = 'create_status_share_flags'
      OR event_name = 'create_status_request_flags'
      OR event_name LIKE 'respond_3p_message_%'
      OR event_name LIKE 'respond_email_%'
      OR event_name = 'respond_statement_flags'
      OR event_name = 'respond_yesno_flags'
      OR event_name = 'respond_multichoice_flags'
      OR event_name = 'respond_location_share_flags'
      OR event_name = 'respond_location_request_flags'
      OR event_name = 'respond_eta_share_flags'
      OR event_name = 'respond_eta_request_flags'
      OR event_name = 'respond_status_share_flags'
      OR event_name = 'respond_status_request_flags'
  )
  WHERE rn = 5
),

aggregated_events AS (
  SELECT
    user_pseudo_id,
    FORMAT_TIMESTAMP('%F %T', DATETIME(MIN(CASE WHEN event_name = 'first_open' THEN TIMESTAMP_MICROS(event_timestamp) END), "CET")) AS step1_first_open,
    FORMAT_TIMESTAMP('%F %T', DATETIME(MIN(CASE WHEN event_name = 'onboarding_step1_registration_complete' THEN TIMESTAMP_MICROS(event_timestamp) END), "CET")) AS step2_registers_account,
    FORMAT_TIMESTAMP('%F %T', DATETIME(MIN(CASE WHEN event_name = 'onboarding_step7_location_complete' THEN TIMESTAMP_MICROS(event_timestamp) END), "CET")) AS step3_provides_permission,
    FORMAT_TIMESTAMP('%F %T', DATETIME(MIN(CASE WHEN event_name LIKE 'integration_created_%' THEN TIMESTAMP_MICROS(event_timestamp) END), "CET")) AS step4_connects_1_integration
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  WHERE
    event_name IN (
      'first_open',
      'onboarding_step1_registration_complete',
      'onboarding_step7_carplay_complete'
    )
    OR event_name LIKE 'integration_created_%'
  GROUP BY
    user_pseudo_id
),

third_integration_event AS (
  SELECT
    user_pseudo_id,
    event_time AS step5_connects_3_integrations
  FROM
    integration_events
  WHERE rn = 3
),

user_location AS (
  SELECT
    user_pseudo_id,
    ANY_VALUE(geo.city) AS location
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  GROUP BY
    user_pseudo_id
),

screen_view_stats AS (
  SELECT
    user_pseudo_id,
    FORMAT_TIMESTAMP('%F %T', DATETIME(MAX(TIMESTAMP_MICROS(event_timestamp)), "CET")) AS last_screen_view,
    COUNTIF(
      TIMESTAMP_MICROS(event_timestamp) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
    ) AS screen_views_last_24h,
    COUNTIF(
      TIMESTAMP_MICROS(event_timestamp) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 48 HOUR)
    ) AS screen_views_last_48h,
    COUNTIF(
      TIMESTAMP_MICROS(event_timestamp) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 72 HOUR)
    ) AS screen_views_last_72h
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`,
    UNNEST(event_params) AS param
  WHERE
    event_name = 'screen_view'
    AND param.key = 'firebase_screen'
    AND param.value.string_value IS NOT NULL
  GROUP BY
    user_pseudo_id
),

user_error_counts AS (
  SELECT
    user_pseudo_id,
    COUNT(*) AS user_error_count
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`
  WHERE
    event_name = 'user_facing_error'
  GROUP BY
    user_pseudo_id
)

SELECT
  ae.user_pseudo_id,
  ou.user_id,
  ae.step1_first_open,
  ul.location,
  svs.last_screen_view,
  svs.screen_views_last_24h,
  svs.screen_views_last_48h,
  svs.screen_views_last_72h,
  ae.step2_registers_account,
  ae.step3_provides_permission,
  ae.step4_connects_1_integration,
  tie.step5_connects_3_integrations,
  me.step6_receives_and_opens_1st_message_or_email,
  ie.step7_sends_1st_email_or_message_or_status_share,
  me10.step8_receives_and_opens_10th_msg_or_email,
  ie5.step9_sends_5th_email_message_status_share,
  IFNULL(ag.step14_is_active_on_day_2, FALSE) AS step14_is_active_on_day_2,
  IFNULL(ag.step15_is_active_on_day_5, FALSE) AS step15_is_active_on_day_5,
  IFNULL(ag.step16_is_active_on_day_10, FALSE) AS step16_is_active_on_day_10,
  IFNULL(ld.step17_days_active_in_last_30_days, 0) AS step17_days_active_in_last_30_days,
  IFNULL(uec.user_error_count, 0) AS user_error_count,
FROM
  aggregated_events ae
LEFT JOIN user_location ul ON ae.user_pseudo_id = ul.user_pseudo_id
LEFT JOIN screen_view_stats svs ON ae.user_pseudo_id = svs.user_pseudo_id
LEFT JOIN third_integration_event tie ON ae.user_pseudo_id = tie.user_pseudo_id
LEFT JOIN message_events me ON ae.user_pseudo_id = me.user_pseudo_id
LEFT JOIN interaction_events ie ON ae.user_pseudo_id = ie.user_pseudo_id
LEFT JOIN message_events_10th me10 ON ae.user_pseudo_id = me10.user_pseudo_id
LEFT JOIN interaction_events_5th ie5 ON ae.user_pseudo_id = ie5.user_pseudo_id
LEFT JOIN aggregated_activity ag ON ae.user_pseudo_id = ag.user_pseudo_id
LEFT JOIN last_30_days_activity ld ON ae.user_pseudo_id = ld.user_pseudo_id
LEFT JOIN (
  SELECT user_pseudo_id, user_id FROM onboarding_user_ids WHERE rn = 1
) ou ON ae.user_pseudo_id = ou.user_pseudo_id
LEFT JOIN user_error_counts uec ON ae.user_pseudo_id = uec.user_pseudo_id
ORDER BY
  ae.step1_first_open DESC
