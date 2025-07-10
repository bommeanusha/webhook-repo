from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["github_events"]
collection = db["events"]

# Home route serving the frontend
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# GitHub Webhook Receiver
@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json
    data = {}

    # Push event
    if event_type == "push":
        data = {
            "type": "push",
            "author": payload["pusher"]["name"],
            "to_branch": payload["ref"].split("/")[-1],
            "timestamp": datetime.now(timezone.utc)
        }

    # Pull Request OPENED
    elif event_type == "pull_request" and payload.get("action") == "opened":
        pr = payload["pull_request"]
        data = {
            "type": "pull_request",
            "author": pr["user"]["login"],
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": datetime.now(timezone.utc)
        }

    # Pull Request CLOSED & MERGED
    elif event_type == "pull_request" and payload.get("action") == "closed" and payload["pull_request"].get("merged"):
        pr = payload["pull_request"]
        data = {
            "type": "merge",
            "author": pr["user"]["login"],
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": datetime.now(timezone.utc)
        }

    else:
        return jsonify({"message": "Ignored or unsupported event type."}), 200

    collection.insert_one(data)
    return jsonify({"message": "Event received"}), 200

# Serve recent events to frontend
@app.route("/events", methods=["GET"])
def get_events():
    events = collection.find().sort("timestamp", -1).limit(10)
    result = []

    for event in events:
        ts = event["timestamp"].strftime("%d %B %Y - %I:%M %p UTC")  # Windows-compatible

        if event["type"] == "push":
            msg = f'{event["author"]} pushed to {event["to_branch"]} on {ts}'
        elif event["type"] == "pull_request":
            msg = f'{event["author"]} submitted a pull request from {event["from_branch"]} to {event["to_branch"]} on {ts}'
        elif event["type"] == "merge":
            msg = f'{event["author"]} merged branch {event["from_branch"]} to {event["to_branch"]} on {ts}'
        else:
            continue

        result.append(msg)

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
