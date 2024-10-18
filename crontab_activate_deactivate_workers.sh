#!/bin/bash

source /home/ubuntu/runpod-monitoring/env/bin/activate
action=$1

if [ "$action" == "activate" ]; then
    python /home/ubuntu/runpod-monitoring/activate_deactivate_workers.py $action
elif [ "$action" == "deactivate" ]; then
    python /home/ubuntu/runpod-monitoring/activate_deactivate_workers.py $action
else
    echo "Argument error. Found arg: $action"
fi