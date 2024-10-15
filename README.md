# Monitoring Tools for MIA

This repository provides tools for monitoring workers and alerting based on activity thresholds.

## 1. **Manage Workers Count Tool**

The **Manage Workers Count Tool** periodically (every 5 minutes) checks the total count of active workers on Runpod. If the total count exceeds the configured threshold, the tool triggers an alert notification on the `runpod_mia_alerts` Slack channel.

### Steps to Run the Tool:

1. Install the required packages.
`pip install -r requirements.txt`

2. Add the following environment variables to the `.env` file. Below is an example, but you will need to replace the placeholder values (`DUMMY_XXXX_ZZZZZZ`) with the correct ones for your environment.

   Example `.env` file:

   ```bash
   API_KEY=DUMMY_XXXX_ZZZZZZ
   SLACK_RUNPOD_ALERT_TOKEN=DUMMY_XXXX_ZZZZZZ
   ACTIVE_WORKER_THRESHOLD=3

3. Run the tool:
   `python manage_workers_count.py`


 
## 2. **Runpod MIA monitoring Tool**
The tool periodically, every 30 minutes, checks the for the availabilty of the MIA tasks and if it fails then it raises
slack alert message for that particular task.

1. Install the required packages.
`pip install -r requirements.txt`

2. Add the following environment variables to the `.env` file. Below is an example, but you will need to replace the placeholder values (`DUMMY_XXXX_ZZZZZZ`) with the correct ones for your environment.

   Example `.env` file:

   ```bash
   SLACK_RUNPOD_ALERT_TOKEN=DUMMY_XXXX_ZZZZZZ
   USER_NAME=DUMMY_XXXX_ZZZZZZ
   PASSWORD=DUMMY_YYYY_ZZZZZZ

3. Run the tool:
   `python monitoring_tool.py`


## 3. Activate Deactivate workers tool.
The tool update (0 to 1 and 1 to 0)  the runpod endpoints active workers at a particular time. The tool is currently triggered via `crontab`

1. Steps to configure crontab
   ```bash
   crontab -e
   00 13 * * * /home/ubuntu/runpod-monitoring/crontab_activate_deactivate_workers.sh activate >> /var/log/deactivate_runpod.log 2>&1

   00 03 * * * /home/ubuntu/runpod-monitoring/crontab_activate_deactivate_workers.sh deactivate >> /var/log/deactivate_runpod.log 2>&1


Activates workers at `13:00 UTC` or `15:00 CET` and Deactivates workers at `03:00 UTC` or `05:00 CET` 
