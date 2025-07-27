"""
Flask-based application to serve specific payload files based on user-agent authentication.

This application checks the user-agent header for a specific prefix and serves
a requested payload file if it exists. Logs all download attempts for auditing.

Dependencies:
- Flask
- waitress
"""

from flask import Flask, request, abort, send_file, render_template
import os
import logging
from datetime import datetime
from waitress import serve

# Create Flask application instance
app = Flask(__name__)

# Configuration parameters
VALID_USER_AGENT_PREFIX = "SpecialAgent"  # Prefix required for user-agent authentication
PAYLOAD_DIR = "payloads"  # Directory where the payload files are stored
LOG_FILE = "access.log"  # File to log access information

# Set up logging to record access attempts
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def log_download(ip, user_agent, payload):
    """
    Logs the details of a successful payload download.

    Args:
        ip (str): The IP address of the client.
        user_agent (str): The user-agent string of the client.
        payload (str): The name of the downloaded payload file.
    """
    logging.info(f"IP: {ip}, User-Agent: {user_agent}, Payload: {payload}")

@app.route('/')
def index():
    """
    Main route of the application.

    - Authenticates requests based on the user-agent header.
    - Serves the requested payload file if authentication is successful.
    - Logs successful download attempts.
    - Renders an `index.html` page if authentication fails.

    Returns:
        Response: The requested payload file or the `index.html` page.
    """
    user_agent = request.headers.get('User-Agent', '')

    # Authentication: Check if user-agent starts with the valid prefix
    if not user_agent.startswith(VALID_USER_AGENT_PREFIX):
        return render_template('index.html')  # Render a fallback page for invalid user-agents

    try:
        # Extract the payload name from the user-agent string
        # Expected format: <PREFIX>:<PAYLOAD_NAME>
        payload_name = None
        if ":" in user_agent:
            payload_name = user_agent.split(":")[1]

        if not payload_name:
            raise ValueError("Payload name missing")

        # Construct the full path to the payload
        payload_path = os.path.join(PAYLOAD_DIR, payload_name)

        # Check if the payload file exists
        if not os.path.exists(payload_path):
            abort(404, "Payload not found")

        # Log the download details
        ip = request.remote_addr
        log_download(ip, user_agent, payload_name)

        # Serve the payload file as an attachment
        return send_file(payload_path, as_attachment=True)

    except Exception as e:
        # Handle errors and return a 400 Bad Request with the error message
        abort(400, str(e))

if __name__ == '__main__':
    """
    Entry point for the application.

    - Ensures the payload directory exists.
    - Uses `waitress` to serve the application in production or testing mode.
    """
    if not os.path.exists(PAYLOAD_DIR):
        os.makedirs(PAYLOAD_DIR)  # Create the payload directory if it doesn't exist

    # Use localhost for testing
    #serve(app, host='127.0.0.1', port=8080)

    # Uncomment the line below to use 0.0.0.0 for production
    serve(app, host='0.0.0.0', port=8080)

"""
Testing Commands:
1. Valid request with an existing payload:
   curl -A "SpecialAgent:payload.bin" "http://127.0.0.1:8080/"

2. Invalid request with an incorrect user-agent:
   curl -A "WrongAgent" "http://127.0.0.1:8080/"

3. Valid user-agent with a nonexistent payload:
   curl -A "SpecialAgent:nonexistent.bin" "http://127.0.0.1:8080/"
"""
