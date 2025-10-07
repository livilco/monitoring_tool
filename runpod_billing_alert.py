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

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="billing_alerts.log",
    filemode="a",
)

api_key = os.environ.get("API_KEY")
slack_channel = "runpod_mia_alerts"
slack_runpod_alert_token = os.environ.get("SLACK_RUNPOD_ALERT_TOKEN")
soft_threshold = float(os.environ.get("SOFT_THRESHOLD"))
hard_threshold = float(os.environ.get("HARD_THRESHOLD"))
lfmh_kill_switch_arn = os.environ.get("LFMH_ICO_RUNPOD_ARN")
nna_kill_switch_arn = os.environ.get("NNA_KILL_SWITCH_ARN")

lfmh_rule_priority_and_arn = [{"RuleArn": lfmh_kill_switch_arn, "Priority": 120}]

nna_rule_priority_and_arn = [{"RuleArn": nna_kill_switch_arn, "Priority": 1}]

client = slack.WebClient(slack_runpod_alert_token)

url = f"https://api.runpod.io/graphql?api_key={api_key}"
headers = {"content-type": "application/json"}

billing_summary_query = {
    "operationName": "getUserBillingSummary",
    "variables": {"input": {"granularity": "DAILY"}},
    "query": """
        query getUserBillingSummary($input: UserBillingInput!) {
          myself {
            billing(input: $input) {
              summary {
                time
                gpuCloudAmount
                cpuCloudAmount
                runpodEndpointAmount
                serverlessAmount
                storageAmount
                __typename
              }
              __typename
            }
            __typename
          }
        }
    """,
}


def send_post_request_to_runpod(query):

    result = {"data": None, "error_message": ""}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(query))
        response.raise_for_status()

        if response.status_code == 200:
            result["data"] = response.json()

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


def get_billing_summary():
    result = send_post_request_to_runpod(billing_summary_query)
    # print(result)

    if result["data"]:
        summary = result["data"]["data"]["myself"]["billing"]["summary"]
        return summary
    else:
        error_message = result["error_message"]
        error_message = (
            "Error during getting endpoints data for activating the endpoints: "
            + error_message
        )
        send_slack_notification(error_message)
        logging.critical(error_message)
        print(error_message)


def get_todays_bill(summary: dict):
    todays_bill = max(
        summary, key=lambda x: datetime.fromisoformat(x["time"].replace("Z", "+00:00"))
    )
    return todays_bill


def compute_todays_cost(todays_bill: dict):
    total_amount = sum(
        value for key, value in todays_bill.items() if key.endswith("Amount")
    )
    return round(total_amount, 2)


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
        result = get_billing_summary()

        if result:
            todays_bill = get_todays_bill(result)
            total_amount = compute_todays_cost(todays_bill)

            if total_amount > hard_threshold:
                alert_message = f"`URGENT: CODE RED` Hard Threshold for a single day spent reached. Amount spent: {total_amount}. Hard Threshod limit is: {hard_threshold}"
                send_slack_notification(alert_message)
                logging.critical(alert_message)

                if not is_kill_switch_activated:
                    # Activate kill switch for LFMH/ICO.
                    lfmh_kill_switch_status = activate_alb_kill_switch(
                        "eu-central-1", lfmh_rule_priority_and_arn
                    )
                    if lfmh_kill_switch_status:
                        alert_message = (
                            f"Runpod LFMH/ICO existing feature kill switch activated."
                        )
                        send_slack_notification(alert_message)
                        logging.critical(alert_message)
                    else:
                        alert_message = f"Runpod UNABLE to ACTIVATE LFMH/ICO existing feature kill switch."
                        send_slack_notification(alert_message)
                        logging.critical(alert_message)

                    # Activate kill switch for NNA
                    nna_kill_switch_status = activate_alb_kill_switch(
                        "us-east-1", nna_rule_priority_and_arn
                    )
                    if nna_kill_switch_status:
                        alert_message = (
                            f"Runpod NNA existing feature kill switch activated."
                        )
                        send_slack_notification(alert_message)
                        logging.critical(alert_message)
                    else:
                        alert_message = f"Runpod UNABLE to ACTIVATE NNA existing feature kill switch."
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
