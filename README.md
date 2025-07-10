# webhook-repo
Flask app to receive GitHub webhooks and display events

# Webhook Receiver App

This is a Flask-based webhook receiver application that listens for GitHub webhook events from a separate `action-repo`. It stores received events into MongoDB and displays them on a minimal UI that updates every 15 seconds.

## Features

- Receives GitHub webhook events: Push, Pull Request, Merge
- Stores event data in MongoDB
- Frontend UI displays recent events (auto-refresh)
- Flask backend using Python
- Uses ngrok for public webhook testing

## Technologies

- Flask
- MongoDB (local)
- Python
- JavaScript
- HTML/CSS

## MongoDB Schema

Each event is stored as:

```json
{
  "type": "push" | "pull_request" | "merge",
  "author": "GitHub username",
  "from_branch": "source_branch (for PR/Merge)",
  "to_branch": "target_branch",
  "timestamp": "UTC time"
}

