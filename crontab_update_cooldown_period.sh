#!/bin/bash

LOGFILE="/tmp/ico_cerebrium_update_cooldown_cron_debug.log"
PYTHON="/home/ubuntu/run_cerebrium_update_cooldown_period/env/bin/python"
SCRIPT="/home/ubuntu/run_cerebrium_update_cooldown_period/cerebrium_update_cooldown_period.py"
COOLDOWNPERIOD=$1

echo "[$(date)] Update cooldown period script triggered by cron with cooldown period: $COOLDOWNPERIOD" >> "$LOGFILE"

# Check if COOLDOWNPERIOD is provided
if [ -z "$COOLDOWNPERIOD" ]; then
    echo "[$(date)] ERROR: No cooldown period provided. Usage: $0 <cooldown_period>" >> "$LOGFILE"
    exit 1
fi

# Check if COOLDOWNPERIOD is an integer
if ! [[ "$COOLDOWNPERIOD" =~ ^[0-9]+$ ]]; then
    echo "[$(date)] ERROR: Invalid cooldown period '$COOLDOWNPERIOD'. It must be an integer." >> "$LOGFILE"
    exit 1
fi

# Check if COOLDOWNPERIOD is >= 30
if [ "$COOLDOWNPERIOD" -lt 30 ]; then
    echo "[$(date)] ERROR: Cooldown period must be at least 30 (provided: $COOLDOWNPERIOD)." >> "$LOGFILE"
    exit 1
fi

echo "[$(date)] Running: $PYTHON $SCRIPT --cooldown-period $COOLDOWNPERIOD" >> "$LOGFILE"
"$PYTHON" "$SCRIPT" --cooldown-period "$COOLDOWNPERIOD" >> "$LOGFILE" 2>&1

# Log exit code
EXITCODE=$?
echo "[$(date)] Python exit code: $EXITCODE" >> "$LOGFILE"
exit $EXITCODE

