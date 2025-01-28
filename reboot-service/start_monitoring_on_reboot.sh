#!/bin/bash

LOG_FILE="/home/ubuntu/debug_startup.log"

echo "[$(date)] Starting tmux sessions..." >> $LOG_FILE 2>&1

/usr/bin/tmux new-session -d -s lfmh-monitoring-tool "cd /home/ubuntu/lfmh-auto-monitoring && source env/bin/activate && /home/ubuntu/lfmh-auto-monitoring/env/bin/python lfmh_monitoring_tool.py"

/usr/bin/tmux new-session -d -s nna-monitoring-tool "cd /home/ubuntu/auto-monitoring && source env/bin/activate && /home/ubuntu/auto-monitoring/env/bin/python monitoring_tool.py"

/usr/bin/tmux new-session -d -s manage-worker-count "cd /home/ubuntu/runpod-monitoring && source env/bin/activate && /home/ubuntu/runpod-monitoring/env/bin/python manage_workers_count.py"

/usr/bin/tmux new-session -d -s mia-staging-backend "cd /home/ubuntu/mia/mia-runpod-backend && docker compose up"

echo "[$(date)] Tmux sessions launched." >> $LOG_FILE 2>&1

