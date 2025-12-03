
# BigQuery User Journey & New User Reports

This folder contains two BigQuery SQL queries and companion notebooks that pull the results, export them to Excel, and push the files to Slack.

## Files
- `V12_user_journey_report.sql`: Builds a wide user journey table from `analytics_470345805.events_intraday_*`, including onboarding milestones, integration creation milestones, messaging send/receive counts, activity-day flags (day 2/5/10, last-30-days), screen view recency, geo city, and user-facing error counts.
- `New_Users_V05.sql`: Captures onboarding funnel timestamps for users whose first open occurred in the last 24 hours (excludes a hard-coded list of test users). Tracks welcome screen, registration, OTP errors, permission grants, paywall impressions/actions, trial start, and first integrations.
- `New_User_Journey_Report.ipynb`: Run every day at 8:30 AM CET time to generate new user report and send it to slack channel `ico-performance-monitoring`. 
- `New_Users_Reports.ipynb`: Run every day at 8:30 AM CET time to generate new user report and send it to slack channel `ico-performance-monitoring`. 


#NOTE: Both the notebooks runs via GCP scheduler. 

## Upload .sql file in GCP Bucket
1. Bump the SQL File Version

Whenever you add new code to an existing .sql file, increment its version number by 1.
Examples:

V12_user_journey_report.sql → V13_user_journey_report.sql

New_Users_V05.sql → New_Users_V06.sql

2. Upload the updated .sql file to the appropriate bucket path:
   | SQL File Type         | GCP Bucket Path                                |
   |`user_journey_report` --> `ico_user_journey_reports/user_journey_query` |
   |`New_Users_report`    --> `ico_new_users_report/new_users_query`        |



3. Update the corresponding Jupyter notebook depending on which .sql file was modified.
   In New_Users_Reports.ipynb
   ```
   blob_name = 'new_users_query/<sql file>'
   ```

   In New_User_Journey_Report.ipynb
   ```
   blob_name = 'user_journey_query/<sql file>'
   ```

   Replace `<sql_file>` with the updated versioned SQL filename.