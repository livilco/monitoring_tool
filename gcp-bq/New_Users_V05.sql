WITH base AS (
  SELECT
    user_pseudo_id,
    user_id,
    event_name,
    event_timestamp,
    geo.city AS location,
    ep.key AS param_key,
    ep.value.string_value AS param_value
  FROM
    `livil-flags-messaging-hub.analytics_470345805.events_intraday_*`,
    UNNEST(event_params) AS ep
),

aggregated AS (
  SELECT
    user_pseudo_id AS User_Pseudo_ID,
    ANY_VALUE(user_id) AS User_ID,
    ANY_VALUE(location) AS Location,

    -- First Open (latest)
    MAX(CASE WHEN event_name = 'first_open'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS First_Open_UTC,

    -- Welcome Screen
    MAX(CASE WHEN event_name = 'screen_view'
                 AND param_key IN ('firebase_screen','firebase_screen_class')
                 AND LOWER(param_value) = 'welcomescreen'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Welcome_Screen,

    -- Registration Info Completed
    MAX(CASE WHEN event_name = 'onboarding_step1_registration_complete'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Registration_Info_Completed,

    -- Error Encountered
    MAX(CASE WHEN event_name = 'onboarding_step2_otp_error_or_invalid'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Error_Encountered,

    -- User Registered
    MAX(CASE WHEN event_name = 'onboarding_step3_phone_verified_start'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS User_Registered,

    -- Permission Push Notification
    MAX(CASE WHEN event_name = 'onboarding_step4_notifications_granted'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Permission_Push_Notification,

    -- Permission Contacts
    MAX(CASE WHEN event_name = 'onboarding_step5_contacts_granted'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Permission_Contacts,

    -- Permission Microphone
    MAX(CASE WHEN event_name = 'onboarding_step6_microphone_granted'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Permission_Microphone,

    -- Permission Location
    MAX(CASE WHEN event_name = 'onboarding_step7_location_granted'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Permission_Location,

    -- Promotion Offered Early Bird
    MAX(CASE WHEN event_name = 'paywall_shown_earlybird'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Promotion_Offered_Early_Bird,

    -- Promotion Tapped
    MAX(CASE WHEN event_name = 'purchase_started_earlybird'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Promotion_Tapped_Early_Bird,

    -- Promotion Subscribed
    MAX(CASE WHEN event_name = 'paywall_subscribed_earlybird'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Promotion_Subscribed_Early_Bird,

    -- Promotion Declined
    MAX(CASE WHEN event_name = 'paywall_closed_earlybird'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Promotion_Declined_Early_Bird,

    -- Onboarding Complete
    MAX(CASE WHEN event_name = 'onboarding_step9_all_done_complete'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Onboarding_Complete,

    -- Integration Page Viewed
    MAX(CASE WHEN event_name = 'screen_view'
                 AND param_key IN ('firebase_screen','firebase_screen_class')
                 AND LOWER(param_value) = 'integrationslistscreen'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Integration_Page_Viewed,

    -- Subscription Wall MS Teams
    MAX(CASE WHEN event_name = 'subscription_wall_triggered_ms_teams'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Subscription_Wall_MS_Teams,

    -- Subscription Wall MS Outlook Email
    MAX(CASE WHEN event_name = 'subscription_wall_triggered_ms_outlook_email'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Subscription_Wall_MS_Outlook_Email,

    -- Subscription Wall MS Outlook Calendar
    MAX(CASE WHEN event_name = 'subscription_wall_triggered_ms_outlook_calendar'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Subscription_Wall_MS_Outlook_Calendar,

    -- Subscription Wall Slack
    MAX(CASE WHEN event_name = 'subscription_wall_triggered_slack'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Subscription_Wall_Slack,

    -- Benefit Explainer Viewed
    MAX(CASE WHEN event_name = 'paywall_shown_upgrade'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Benefit_Explainer_Viewed,

    -- Trial Started
    MAX(CASE WHEN event_name = 'paywall_subscribed_upgrade'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Trial_Started,

    -- Integration Events
    MAX(CASE WHEN event_name = 'integration_created_msteams'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Integration_MS_Team,
    MAX(CASE WHEN event_name = 'integration_created_outlookemail'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Integration_MS_Outlook_Email,
    MAX(CASE WHEN event_name = 'integration_created_outlookcalendar'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Integration_MS_Outlook_Calendar,
    MAX(CASE WHEN event_name = 'integration_created_slack'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Integration_Slack,
    MAX(CASE WHEN event_name = 'integration_created_gmailemail'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Integration_Gmail,
    MAX(CASE WHEN event_name = 'integration_created_googlecalendar'
             THEN TIMESTAMP_MICROS(event_timestamp) END) AS Integration_Google_Calendar

  FROM base
  GROUP BY user_pseudo_id
)

SELECT
  User_Pseudo_ID,
  User_ID,
  Location,
  FORMAT_TIMESTAMP('%F %T', DATETIME(First_Open_UTC, "CET")) AS First_Open,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Welcome_Screen, "CET")) AS Welcome_Screen,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Registration_Info_Completed, "CET")) AS Registration_Info_Completed,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Error_Encountered, "CET")) AS Error_Encountered,
  FORMAT_TIMESTAMP('%F %T', DATETIME(User_Registered, "CET")) AS User_Registered,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Permission_Push_Notification, "CET")) AS Permission_Push_Notification,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Permission_Contacts, "CET")) AS Permission_Contacts,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Permission_Microphone, "CET")) AS Permission_Microphone,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Permission_Location, "CET")) AS Permission_Location,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Promotion_Offered_Early_Bird, "CET")) AS Promotion_Offered_Early_Bird,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Promotion_Tapped_Early_Bird, "CET")) AS Promotion_Tapped_Early_Bird,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Promotion_Subscribed_Early_Bird, "CET")) AS Promotion_Subscribed_Early_Bird,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Promotion_Declined_Early_Bird, "CET")) AS Promotion_Declined_Early_Bird,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Onboarding_Complete, "CET")) AS Onboarding_Complete,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Integration_Page_Viewed, "CET")) AS Integration_Page_Viewed,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Subscription_Wall_MS_Teams, "CET")) AS Subscription_Wall_MS_Teams,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Subscription_Wall_MS_Outlook_Email, "CET")) AS Subscription_Wall_MS_Outlook_Email,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Subscription_Wall_MS_Outlook_Calendar, "CET")) AS Subscription_Wall_MS_Outlook_Calendar,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Subscription_Wall_Slack, "CET")) AS Subscription_Wall_Slack,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Benefit_Explainer_Viewed, "CET")) AS Benefit_Explainer_Viewed,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Trial_Started, "CET")) AS Trial_Started,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Integration_MS_Team, "CET")) AS Integration_MS_Team,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Integration_MS_Outlook_Email, "CET")) AS Integration_MS_Outlook_Email,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Integration_MS_Outlook_Calendar, "CET")) AS Integration_MS_Outlook_Calendar,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Integration_Slack, "CET")) AS Integration_Slack,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Integration_Gmail, "CET")) AS Integration_Gmail,
  FORMAT_TIMESTAMP('%F %T', DATETIME(Integration_Google_Calendar, "CET")) AS Integration_Google_Calendar
FROM aggregated
WHERE First_Open_UTC >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND (User_ID is NULL OR User_ID NOT IN (
    '8ae1402512b43fa1073917ed960efb5c2491',
    'cc18016b53638c93a72fd21e6442d6fee7e4',
    'a2ec2145e537352c5185825ceda0ba1b2299',
    '42004d0357e13415dc1b157fa87a153b44d7',
    'dea444d59748e2be06d8676f4b1a6fbb99a0',
    '4b2292631d72d29ea27f8c96311cc47b6a31',
    '20a80d877165fefd66801684e0ca9acccdbc',
    '85fbbcd4e8777b81aa9fd48b83306d5d2d88',
    '63fa11f24251201e0066061374626c9792fa',
    'f8ad70e77c2ab67d3430f7fa6d5b7e61db85',
    '5cc38dcc0f73e4fbee796592aa760c4df198',
    'd5b7fe1d9dacd53cdd8f23b2b36fde6550c2',
    '0a2bbeaf8faefcdeeb9b4d93a1b6881b0e4e',
    '989ad1d35c9bb48badec91fa9ead52d9266a',
    '766902a3a1e0f034657f69db09ea4e76f038',
    '7f7586eea893af4b7826108fb7e25be9bec2',
    'efb2a27b0959aa61209943911b40a0759e7a',
    'f0d90b82d01b92d6ad0c15c4d045e01a1896',
    '353406cb5e569aa7ca57bb1968448bbb57db',
    '1b570e77a0e2675576503975814ddd1bce8a',
    '06c5da0e6e6fcefb5c29c07fc1922bc9c923',
    'cc36fbb14b107255c1a1ee3b9b7b05e38704',
    'c209ca59b18d9ea4ea421adb6b742a9790d8',
    '1fb9285c9416f472482d8bfbbd155b43ca5d',
    '574f45442d682f6ba99f9754b3c3cfca8dc6',
    '230b6f96545a8f9710c101365a847bac5878',
    '4846ab6c3114792a9a60a465ca605a865b28',
    '46d3c5c806b8db639a8bb774b98e6846e218',
    '3b5af315ba807428f184425eb8fe687d764c',
    '0261769222e688ab7e4160e30bad356b2af3',
    'ca5bb49a8b5e056848609079753cf8471ab5'

  ))
ORDER BY First_Open_UTC DESC;