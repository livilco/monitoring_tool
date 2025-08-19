import slack
import os
from dotenv import load_dotenv
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
import time
from datetime import datetime
import boto3
import botocore.exceptions
from datetime import date

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="cerebrium_billing_alerts.log",
    filemode="a",
)

token = os.environ.get("API_KEY")
slack_channel = "cerebrium-monitoring"
slack_runpod_alert_token = os.environ.get("SLACK_ALERT_TOKEN")
soft_threshold = float(os.environ.get("SOFT_THRESHOLD"))
hard_threshold = float(os.environ.get("HARD_THRESHOLD"))

lfmh_kill_switch_arn = os.environ.get("LFMH_KILL_SWITCH_ARN")
nna_kill_switch_arn = os.environ.get("NNA_KILL_SWITCH_ARN")

lfmh_rule_priority_and_arn = [{"RuleArn": lfmh_kill_switch_arn, "Priority": 5}]

nna_rule_priority_and_arn = [{"RuleArn": nna_kill_switch_arn, "Priority": 5}]

client = slack.WebClient(slack_runpod_alert_token)

url = "https://rest.cerebrium.ai/v2/projects/p-83a7fa9e/apps/p-83a7fa9e-content-importance/cost"

headers = {"Authorization": f"Bearer {token}"}


def send_post_request_to_cerebrium(url):

    result = {"data": None, "error_message": ""}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            result["data"] = response.json()

        # print(result)

        return result

    except requests.exceptions.HTTPError as e:
        logging.critical(f"HTTP Error happend: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.ConnectionError as e:
        logging.critical(f"HTTP Connection error happend: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.Timeout as e:
        logging.critical(f"Timeout error happend: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.RequestException as e:
        logging.critical(f"Timeout error happend: {str(e)}")
        result["error_message"] = str(e)
        return result


def get_today_total_cost_dollars(data: dict) -> float:

    try:
        today_str = date.today().strftime("%Y-%m-%d")
        costs = data.get("costs", {})

        if today_str not in costs:
            error_message = f"Cerebrium No cost data found for date {today_str}"
            send_slack_notification(error_message)
            logging.critical(error_message)

        total_cost_cents = costs[today_str].get("total_cost_cents", 0.0)
        return round(total_cost_cents / 100, 2)  # Convert cents to dollars

    except Exception as e:
        error_message = f"Error: {e}"
        send_slack_notification(error_message)
        logging.critical(error_message)
        return 0.0


def send_slack_notification(message):
    try:
        client.chat_postMessage(channel=slack_channel, text=message)
    except slack.errors.SlackApiError as e:
        if e.response["error"] == "not_in_channel":
            # Attempt to join the channel first
            try:
                client.conversations_join(channel=slack_channel)
                client.chat_postMessage(channel=slack_channel, text=error_message)
            except slack.errors.SlackApiError as join_error:
                print(
                    f"Failed to join and send message: {join_error.response['error']}"
                )
        else:
            print(f"Slack API Error: {e.response['error']}")


def activate_alb_kill_switch(region_name, rule_priority_and_arn):
    try:
        # Initialize the ELBv2 client
        client = boto3.client("elbv2", region_name=region_name)

        response = client.set_rule_priorities(RulePriorities=rule_priority_and_arn)

        print(f"Kill Switch activated!! region_name: {region_name}")
        return True
        # print(response)

    except botocore.exceptions.NoCredentialsError:
        logging.critical(
            "Error: No AWS credentials found. Please configure them using 'aws configure' or set environment variables."
        )

    except botocore.exceptions.PartialCredentialsError:
        logging.critical(
            "Error: Incomplete AWS credentials detected. Please check your AWS access key and secret key."
        )

    except botocore.exceptions.ClientError as e:
        # Handle specific AWS errors
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        logging.critical(f"AWS ClientError: {error_code} - {error_message}")

    except botocore.exceptions.EndpointConnectionError:
        logging.critical(
            "Error: Unable to connect to AWS endpoint. Check your internet connection and region settings."
        )

    except Exception as e:
        logging.critical(f"An unexpected error occurred: {str(e)}")

    return False


def start_monitoring(sleep):

    is_kill_switch_activated = False

    while True:
        result = send_post_request_to_cerebrium(url)
        # print(result)

        if result:
            total_amount = get_today_total_cost_dollars(result["data"])
            # print(f"{total_amount=}")

            if total_amount > hard_threshold:
                alert_message = f"`URGENT: CODE RED` Hard Threshold for a single day spent reached. Amount spent: {total_amount}. Hard Threshod limit is: {hard_threshold}"
                # print(f"{alert_message=}")
                send_slack_notification(alert_message)
                logging.critical(alert_message)

                if not is_kill_switch_activated:
                    # Activate Cerebrium kill switch for LFMH/ICO.
                    lfmh_kill_switch_status = activate_alb_kill_switch(
                        "eu-central-1", lfmh_rule_priority_and_arn
                    )
                    if lfmh_kill_switch_status:
                        alert_message = f"Cerebrium LFMH/ICO Application load balancer kill switch activated."
                        send_slack_notification(alert_message)
                        logging.critical(alert_message)
                    else:
                        alert_message = f"Cerebrium UNABLE to ACTIVATE LFMH/ICO Application load balancer kill switch."
                        send_slack_notification(alert_message)
                        logging.critical(alert_message)

                    # Activate Cerebrium kill switch for NNA
                    nna_kill_switch_status = activate_alb_kill_switch(
                        "us-east-1", nna_rule_priority_and_arn
                    )
                    if nna_kill_switch_status:
                        alert_message = f"Cerebrium NNA Application load balancer kill switch activated."
                        send_slack_notification(alert_message)
                        logging.critical(alert_message)
                    else:
                        alert_message = f"Cerebrium UNABLE to ACTIVATE NNA Application load balancer kill switch."
                        send_slack_notification(alert_message)
                        logging.critical(alert_message)

                    if lfmh_kill_switch_status and nna_kill_switch_status:
                        is_kill_switch_activated = True

            elif total_amount > soft_threshold:
                alert_message = f"`ALERT`: Soft threshold reached. Current Amount spent: `${total_amount}`. Soft threshold is set to: `${soft_threshold}`"
                send_slack_notification(alert_message)
                logging.critical(alert_message)
            else:
                pass

        else:
            error_message = f"Error occured: {result}"
            send_slack_notification(error_message)
            logging.critical(error_message)
            print(error_message)

        # sleep for 1 mins.
        time.sleep(sleep)


start_monitoring(60)
