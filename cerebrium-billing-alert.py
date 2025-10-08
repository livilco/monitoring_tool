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

token_p83a7fa9e = os.environ.get("API_KEY_P83A7FA9E")
token_p87ef9251 = os.environ.get("API_KEY_P87EF9251")
token_pde09db61 = os.environ.get("API_KEY_PDE09DB61")
slack_channel = "cerebrium-monitoring"
slack_runpod_alert_token = os.environ.get("SLACK_ALERT_TOKEN")
soft_threshold = float(os.environ.get("SOFT_THRESHOLD"))
hard_threshold = float(os.environ.get("HARD_THRESHOLD"))


cerebrium_existing_feat_arn = os.environ.get("CEREBRIUM_EXISTING_FEATURE")
cerebrium_new_feat_arn = os.environ.get("CEREBRIUM_NEW_FEATURE")

cerebrium_existing_rule_priority_and_arn = [{"RuleArn": cerebrium_existing_feat_arn, "Priority": 150}]
cerebrium_new_feat_rule_priority_and_arn = [{"RuleArn": cerebrium_new_feat_arn, "Priority": 160}]

client = slack.WebClient(slack_runpod_alert_token)

url_content_impo = "https://rest.cerebrium.ai/v2/projects/p-83a7fa9e/apps/p-83a7fa9e-content-importance/cost"
url_cmd_interpreter = "https://rest.cerebrium.ai/v2/projects/p-83a7fa9e/apps/p-83a7fa9e-command-interpreter/cost"

url_message_improv = "https://rest.cerebrium.ai/v2/projects/p-de09db61/apps/p-de09db61-message-improvisation/cost"

url_smart_reply = (
    "https://rest.cerebrium.ai/v2/projects/p-87ef9251/apps/p-87ef9251-smart-reply/cost"
)
url_summarization = "https://rest.cerebrium.ai/v2/projects/p-87ef9251/apps/p-87ef9251-summarization/cost"

app_dict = {
    url_content_impo: token_p83a7fa9e,
    url_cmd_interpreter: token_p83a7fa9e,
    url_message_improv: token_pde09db61,
    url_smart_reply: token_p87ef9251,
    url_summarization: token_p87ef9251,
}


def send_post_request_to_cerebrium(url, token):

    headers = {"Authorization": f"Bearer {token}"}

    result = {"data": None, "error_message": ""}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            result["data"] = response.json()

        # print(result)

        return result

    except requests.exceptions.HTTPError as e:
        logging.critical(f"HTTP Error happened: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.ConnectionError as e:
        logging.critical(f"HTTP Connection error happened: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.Timeout as e:
        logging.critical(f"Timeout error happened: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.RequestException as e:
        logging.critical(f"Timeout error happened: {str(e)}")
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
            return 0.0

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
                client.chat_postMessage(channel=slack_channel, text=message)
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
        total_cost = 0.0
        for url, token in app_dict.items():
            result = send_post_request_to_cerebrium(url, token)
            # print(result)
            if result:
                app_cost = get_today_total_cost_dollars(result["data"])
                total_cost = total_cost + app_cost
            # print(f"{total_cost=}")
            else:
                error_message = f"Error occured: {result}"
                send_slack_notification(error_message)
                logging.critical(error_message)
                print(error_message)

        if total_cost > hard_threshold:
            alert_message = f"`URGENT: CODE RED` Hard Threshold for a single day spent reached. Amount spent: {total_cost}. Hard Threshod limit is: {hard_threshold}"
            # print(f"{alert_message=}")
            send_slack_notification(alert_message)
            logging.critical(alert_message)

            if not is_kill_switch_activated:
                # Activate cerebrium kill switch for Existing feature LFMH/ICO.
                existing_feat_kill_switch_status = activate_alb_kill_switch(
                    "eu-central-1", cerebrium_existing_rule_priority_and_arn
                )
                if existing_feat_kill_switch_status:
                    alert_message = f"Cerebrium LFMH/ICO existing feature kill switch activated."
                    send_slack_notification(alert_message)
                    logging.critical(alert_message)
                else:
                    alert_message = f"Cerebrium UNABLE to ACTIVATE LFMH/ICO existing feature kill switch."
                    send_slack_notification(alert_message)
                    logging.critical(alert_message)

                # Activate Cerebrium kill switch for new features.
                new_feat_kill_switch_status = activate_alb_kill_switch(
                    "eu-central-1", cerebrium_new_feat_rule_priority_and_arn
                )
                if new_feat_kill_switch_status:
                    alert_message = f"Cerebrium new feature kill switch activated."
                    send_slack_notification(alert_message)
                    logging.critical(alert_message)
                else:
                    alert_message = f"Cerebrium UNABLE to ACTIVATE new feature kill switch."
                    send_slack_notification(alert_message)
                    logging.critical(alert_message)

                if existing_feat_kill_switch_status and new_feat_kill_switch_status:
                    is_kill_switch_activated = True

        elif total_cost > soft_threshold:
            alert_message = f"`ALERT`: Soft threshold reached. Current Amount spent: `${total_cost}`. Soft threshold is set to: `${soft_threshold}`"
            send_slack_notification(alert_message)
            logging.critical(alert_message)
        else:
            pass

        # sleep for 1 mins.
        time.sleep(sleep)


start_monitoring(60)
