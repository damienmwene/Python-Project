import requests
import time
import os
import logging
import threading

from flask import Flask, render_template, request, jsonify

# ----------------------------------
# Flask App
# ----------------------------------
app = Flask(__name__)

# ----------------------------------
# Logging
# ----------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("uptime.log")
    ]
)

# ----------------------------------
# URLs to Monitor
# ----------------------------------
URLS = [
    "https://www.google.com",
    "https://auu5wso6vs2eev42dwt47b35he0geulm.lambda-url.us-east-1.on.aws"
]

# ----------------------------------
# Slack Webhook
# ----------------------------------
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# ----------------------------------
# Dashboard Data
# ----------------------------------
monitor_results = []

# ----------------------------------
# Slack Alert
# ----------------------------------
def send_slack_alert(url):
    if not SLACK_WEBHOOK_URL:
        logging.warning("Slack webhook URL not configured.")
        return

    message = {
        "text": f":red_circle: ALERT: {url} is DOWN!"
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=message
        )

        if response.status_code != 200:
            logging.warning(
                f"Slack alert failed: {response.text}"
            )

    except Exception as e:
        logging.error(
            f"Slack alert error: {e}"
        )

# ----------------------------------
# Check Website
# ----------------------------------
def check_website(url):
    try:
        start = time.time()

        response = requests.get(
            url,
            timeout=5
        )

        response_time = round(
            (time.time() - start) * 1000
        )

        return (
            response.status_code == 200,
            response_time
        )

    except requests.exceptions.RequestException:
        return False, 0

# ----------------------------------
# Monitoring Loop
# ----------------------------------
def monitor():

    global monitor_results

    while True:

        results = []

        for url in URLS:

            status, response_time = check_website(url)

            status_str = (
                "UP"
                if status
                else "DOWN"
            )

            logging.info(
                f"{url} is {status_str}"
            )

            if not status:
                send_slack_alert(url)

            results.append({
                "url": url,
                "status": status_str,
                "response_time": response_time
            })

        monitor_results = results

        logging.info(
            f"Completed checks for {len(URLS)} URLs"
        )

        time.sleep(60)

# ----------------------------------
# Dashboard Route
# ----------------------------------
@app.route("/")
def dashboard():

    up_count = len([
        x for x in monitor_results
        if x["status"] == "UP"
    ])

    down_count = len([
        x for x in monitor_results
        if x["status"] == "DOWN"
    ])

    return render_template(
        "dashboard.html",
        monitors=monitor_results,
        up_count=up_count,
        down_count=down_count
    )

@app.route("/about")
def about():
    # provide counts to the about page for dynamic status display
    up_count = len([x for x in monitor_results if x["status"] == "UP"])
    down_count = len([x for x in monitor_results if x["status"] == "DOWN"])

    return render_template("about.html", up_count=up_count, down_count=down_count)


@app.route('/add-monitor', methods=['POST'])
def add_monitor():
    """Add a new monitor URL. Accepts JSON {"url": "https://..."} or form data.
    Returns JSON with current status for that URL.
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    url = data.get('url') if data else None

    if not url:
        return jsonify({"ok": False, "error": "no url provided"}), 400

    # ensure scheme
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    # avoid duplicates
    if url not in URLS:
        URLS.append(url)

    # perform an immediate check and update monitor_results
    status_bool, response_time = check_website(url)
    status_str = 'UP' if status_bool else 'DOWN'

    # update existing entry if present
    found = False
    for m in monitor_results:
        if m.get('url') == url:
            m['status'] = status_str
            m['response_time'] = response_time
            found = True
            break

    if not found:
        monitor_results.append({
            'url': url,
            'status': status_str,
            'response_time': response_time
        })

    return jsonify({"ok": True, "url": url, "status": status_str, "response_time": response_time})


@app.route('/remove-monitor', methods=['POST', 'DELETE'])
def remove_monitor():
    """Remove a monitor URL. Accepts JSON {"url": "https://..."} or form data.
    Returns JSON acknowledging removal.
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    url = data.get('url') if data else None

    if not url:
        return jsonify({"ok": False, "error": "no url provided"}), 400

    # normalize scheme
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    # remove from URLS list
    try:
        while url in URLS:
            URLS.remove(url)
    except ValueError:
        pass

    # remove from monitor_results
    global monitor_results
    monitor_results = [m for m in monitor_results if m.get('url') != url]

    return jsonify({"ok": True, "url": url})

# ----------------------------------
# Health Endpoint
# ----------------------------------
@app.route("/health")
def health():
    return {
        "status": "UP"
    }

# ----------------------------------
# Main
# ----------------------------------
if __name__ == "__main__":

    # Initial check before starting Flask
    initial_results = []

    for url in URLS:

        status, response_time = check_website(url)

        initial_results.append({
            "url": url,
            "status": "UP" if status else "DOWN",
            "response_time": response_time
        })

    monitor_results = initial_results

    # Background monitoring thread
    monitor_thread = threading.Thread(
        target=monitor,
        daemon=True
    )

    monitor_thread.start()

    app.run(
        host="0.0.0.0",
        port=5000
    )