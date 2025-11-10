#!/bin/bash

LOGFILE="/tmp/ico_cron_debug.log"
PYTHON="/home/ubuntu/ico-activate-deactivate/env/bin/python"
SCRIPT="/home/ubuntu/ico-activate-deactivate/activate_deactivate_workers.py"
ACTION=$1

echo "[$(date)] Script triggered by cron with action: $ACTION" >> "$LOGFILE"

if [ "$ACTION" == "activate" ] || [ "$ACTION" == "deactivate" ]; then
    echo "[$(date)] Running: $PYTHON $SCRIPT $ACTION" >> "$LOGFILE"
    "$PYTHON" "$SCRIPT" "$ACTION" >> "$LOGFILE" 2>&1
    echo "[$(date)] Python exit code: $?" >> "$LOGFILE"
else
    echo "[$(date)] ERROR: Invalid action argument: $ACTION" >> "$LOGFILE"
fi
