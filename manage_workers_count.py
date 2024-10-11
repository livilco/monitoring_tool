import requests
import json
import slack
import os
from dotenv import load_dotenv
import logging
import time

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="runpod_worker_count.log",
    filemode="a",
)

api_key = os.environ.get("API_KEY")
active_worker_threshold = int(os.environ.get("ACTIVE_WORKER_THRESHOLD"))
slack_channel = "runpod_mia_alerts"
slack_runpod_alert_token = os.environ.get("SLACK_RUNPOD_ALERT_TOKEN")

client = slack.WebClient(slack_runpod_alert_token)

url = f"https://api.runpod.io/graphql?api_key={api_key}"
headers = {"content-type": "application/json"}

query = {
    "query": """
    query Endpoints {
      myself {
        endpoints {
          workersMin
        }
      }
    }
    """
}


def get_endpoints_data():

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


def get_activeworkers_and_endpoints_count(data):

    endpoints = data["data"]["myself"]["endpoints"]
    total_endpoints = len(endpoints)

    total_active_workers = sum(endpoint.get("workersMin", 0) for endpoint in endpoints)

    return total_endpoints, total_active_workers


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


def start_monitoring(sleep):

    while True:
        result = get_endpoints_data()

        if result["data"]:
            total_endpoints, total_active_workers = (
                get_activeworkers_and_endpoints_count(result['data'])
            )

            # Check for the threshold
            if total_active_workers > active_worker_threshold:
                alert_msg = f" Active worker count is: `{total_active_workers}` which more than the threshold configured i.e. `{active_worker_threshold}`. Total number of endpoints: `{total_endpoints}`"
                send_slack_notification(alert_msg)
                logging.critical(alert_msg)
                print(alert_msg)
        else:
            error_message = result["error_message"]
            send_slack_notification(error_message)
            logging.critical(error_message)
            print(error_message)

        # sleep for 5 mins.
        time.sleep(sleep)


start_monitoring(300)

