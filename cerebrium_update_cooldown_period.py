import requests
import slack
import os
from dotenv import load_dotenv
import logging
import argparse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="cerebrium_update_cooldown_period.log",
    filemode="a",
)

slack_channel = "cerebrium-monitoring"
slack_cerebrium_token = os.environ.get("SLACK_CEREBRIUM_TOKEN")
message_improv_url = os.environ.get("MESSAGE_IMPROV_URL")
email_improv_url = os.environ.get("EMAIL_IMPROV_URL")
summarization_url = os.environ.get("SUMMARIZATION_URL")
smart_reply_url = os.environ.get("SMART_REPLY_URL")
api_key_PDE09DB61 = os.environ.get("API_KEY_PDE09DB61")
api_key_PF875AC4E = os.environ.get("API_KEY_PF875AC4E")

client = slack.WebClient(slack_cerebrium_token)

app_dict = {
    message_improv_url: api_key_PDE09DB61,
    email_improv_url: api_key_PDE09DB61,
    summarization_url: api_key_PF875AC4E,
    smart_reply_url: api_key_PF875AC4E,
}


def update_cooldown_period(coldown_period):
    for app_url, api_key in app_dict.items():
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {"cooldownPeriodSeconds": coldown_period}
        try:
            response = requests.patch(app_url, json=payload, headers=headers)
            response.raise_for_status()
            #print(f"Response from {app_url}: {response.status_code} - {response.text}")

            if response.status_code == 200:
                success_msg = f"Successfully updated cooldown period to `{coldown_period} seconds` for {app_url}"
                logging.info(success_msg)
                print(success_msg)
                send_slack_notification(success_msg)

        except requests.exceptions.HTTPError as e:
            err_msg = f"HTTP error occurred while updating {app_url}: {e}"
            logging.critical(err_msg)
            print(err_msg)
            send_slack_notification(err_msg)

        except requests.exceptions.ConnectionError as e:
            err_msg = f"Connection error occurred while updating {app_url}: {e}"
            logging.critical(err_msg)
            print(err_msg)
            send_slack_notification(err_msg)

        except requests.exceptions.Timeout as e:
            err_msg = f"Timeout error occurred while updating {app_url}: {e}"
            logging.critical(err_msg)
            print(err_msg)
            send_slack_notification(err_msg)

        except requests.exceptions.RequestException as e:
            err_msg = f"An error occurred while updating {app_url}: {e}"
            logging.critical(err_msg)
            print(err_msg)
            send_slack_notification(err_msg)


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
                logging.critical(
                    f"Failed to join and send message: {join_error.response['error']}"
                )
        else:
            print(f"Slack API Error: {e.response['error']}")
            logging.critical(f"Slack API Error: {e.response['error']}")


def positive_int(value):
    try:
        iv = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer value: {value}")
    if iv < 30:
        raise argparse.ArgumentTypeError("Cooldown period must be >= 30 seconds.")

    return iv


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            description="Update Cerebrium Cooldown Period."
        )
        # add condition that cooldown period should be grater than 0.
        parser.add_argument(
            "--cooldown-period",
            type=positive_int,
            required=True,
            help="Cooldown period in seconds (must be >= 30 seconds)",
        )
        args = parser.parse_args()

        cooldown_period = args.cooldown_period
        print(f"Updating Cerebrium cooldown period to {cooldown_period} seconds.")
        logging.info(
            f"Updating Cerebrium cooldown period to {cooldown_period} seconds."
        )
        update_cooldown_period(cooldown_period)

    except Exception as e:
        err_msg = f"Error parsing arguments: {e}"
        logging.critical(err_msg)
        print(err_msg)
        exit(1)
