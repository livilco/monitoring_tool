
# BigQuery User Journey & New User Reports

This folder contains two BigQuery SQL queries and companion notebooks that pull the results, export them to Excel, and push the files to Slack.

## Files
- `V12_user_journey_report.sql`: Builds a wide user journey table from `analytics_470345805.events_intraday_*`, including onboarding milestones, integration creation milestones, messaging send/receive counts, activity-day flags (day 2/5/10, last-30-days), screen view recency, geo city, and user-facing error counts.
- `New_Users_V05.sql`: Captures onboarding funnel timestamps for users whose first open occurred in the last 24 hours (excludes a hard-coded list of test users). Tracks welcome screen, registration, OTP errors, permission grants, paywall impressions/actions, trial start, and first integrations.
- `New_User_Journey_Report.ipynb`: Run every day at 8:30 AM CET time to generate new user report and send it to slack channel `ico-performance-monitoring`. 
- `New_Users_Reports.ipynb`: Run every day at 8:30 AM CET time to generate new user report and send it to slack channel `ico-performance-monitoring`. 


#NOTE: Both the notebooks runs via GCP scheduler. 

