import requests
from requests.auth import HTTPBasicAuth
import logging
from var import (
    summary_input,
    pickup_intent_input,
    smart_reply_input,
    email_smart_reply_input,
    message_generation_input,
    message_improvisation_input,
    email_generation_input,
    email_improvisation_input,
)
import time
import slack
import os
from dotenv import load_dotenv
import json

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="app.log",
    filemode="a",
)

timeout = 120
# url = "https://mia-staging.livil.co"
url = "https://us.mia.livil.co"
slack_channel = "nna_mia_alerts"
slack_lfmh_alert_token = os.environ.get("SLACK_NNA_ALERT_TOKEN")
username = os.environ.get("USER_NAME")
password = os.environ.get("PASSWORD")
jwt_token = os.environ.get("JWT_TOKEN")

client = slack.WebClient(slack_lfmh_alert_token)


def send_request_to_mia(
    data,
    task: str,
):
    endpoint = "/insights_ico"
    full_url = url + endpoint
    result = {"is_success": False, "error_message": "Default"}

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "X-provider": "runpod",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(full_url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        response_dict = response.json()
        error = response_dict["res_jobs"][0]["error"]

        # When the request is in 'IN_QUEUE' or 'IN_PROGRESS' state on the runpod side for a
        # very long time then the backend sends HTTP 200 with the error message.
        # For now to capture such scenario a simple string matching will work.
        # Once the 'error' key is added to JSON response for all the tasks then
        # below logic we have to change the below logic.
        if response.status_code == 200 and not error:
            logging.info(f"Response: {response_dict}")
            print(f"Response: {response_dict}")
            result["is_success"] = True
            result["error_message"] = ""
            return result
        else:
            logging.info(f"Response: {response_dict}")
            print(f"Response: {response_dict}")
            result["is_success"] = False
            result["error_message"] = error
            return result

    except requests.exceptions.HTTPError as e:
        logging.critical(f"HTTP Error happend for {task} and exception {str(e)}")
        result["is_success"] = False
        result["error_message"] = str(e)
        return result

    except requests.exceptions.ConnectionError as e:
        logging.critical(
            f"HTTP Connection error happend for {task} and exception {str(e)}"
        )
        result["is_success"] = False
        result["error_message"] = str(e)
        return result

    except requests.exceptions.Timeout as e:
        logging.critical(f"Timeout error happend for {task} and exception {str(e)}")
        result["is_success"] = False
        result["error_message"] = str(e)
        return result

    except requests.exceptions.RequestException as e:
        logging.critical(f"Timeout error happend for {task} and exception {str(e)}")
        result["is_success"] = False
        result["error_message"] = str(e)
        return result


def check_summarization(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {"id": req_id, "input_text": summary_input, "model": model, "task": task}
        ]
    }

    return send_request_to_mia(data, task)


def check_pickup_intent(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": pickup_intent_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_mia(data, task)


def check_smart_reply(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": smart_reply_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_mia(data, task)


def check_email_smart_reply(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": email_smart_reply_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_mia(data, task)


def check_message_generation(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": message_generation_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_mia(data, task)


def check_message_improvisation(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": message_improvisation_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_mia(data, task)


def check_email_generation(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": email_generation_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_mia(data, task)


def check_email_improvisation(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": email_improvisation_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_mia(data, task)


def send_slack_notification(error_message):
    try:
        client.chat_postMessage(channel=slack_channel, text=error_message)
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
        result = check_summarization("jupiter-1", "summarization")

        if not result["is_success"]:
            message = f"Summarization is not working: {result['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)

        output = check_smart_reply("jupiter-2", "smart-reply")
        if not output["is_success"]:
            message = f"Smart reply is not working: {output['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)

        result = check_pickup_intent("jupiter-2", "pickup-intent")
        if not result["is_success"]:
            message = f"Pickup-intent is not working: {result['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)

        result = check_email_smart_reply("jupiter-2", "email-smart-reply")
        if not result["is_success"]:
            message = f"Email smart reply is not working: {result['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)

        result = check_message_generation("jupiter-2", "message-generation")
        if not result["is_success"]:
            message = f"Message generation is not working: {result['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)

        result = check_message_improvisation("jupiter-2", "message-improvisation")
        if not result["is_success"]:
            message = (
                f"Message improvisation is not working: {result['error_message']} "
            )
            send_slack_notification(message)

        time.sleep(sleep)

        result = check_email_generation("jupiter-2", "email-generation")
        if not result["is_success"]:
            message = f"Email generation is not working: {result['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)

        result = check_email_improvisation("jupiter-2", "email-improvisation")
        if not result["is_success"]:
            message = f"Email improvisation is not working: {result['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)


# send_slack_notification("This is a test message")

start_monitoring(300)
