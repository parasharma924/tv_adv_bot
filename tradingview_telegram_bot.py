"""
TradingView to Telegram Alert Bot
Receives webhook alerts from TradingView and sends them to Telegram
"""

from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# ============= CONFIGURATION =============
# These will be set as environment variables in Render
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8523623199:AAH8MbUcBOxicEE1wvResOqTRu67lpEBOb4")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1003998592148")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "2048")
PORT = int(os.environ.get("PORT", 5000))

# Trading Hours Configuration (in 24-hour format)
TRADING_START_HOUR = int(os.environ.get("TRADING_START_HOUR", "9"))   # Default: 9 AM
TRADING_END_HOUR = int(os.environ.get("TRADING_END_HOUR", "16"))      # Default: 4 PM (16:00)
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")                 # Your timezone
# =========================================

# Import timezone support
from datetime import datetime
import pytz


def send_telegram_message(message):
    """Send a message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"  # Allows basic formatting
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return None


@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive webhook from TradingView"""
    try:
        # Get the data from TradingView
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Optional: Check secret key for security
        secret = request.args.get('secret', '')
        if WEBHOOK_SECRET and secret != WEBHOOK_SECRET:
            return jsonify({"status": "error", "message": "Invalid secret"}), 403
        
        # Format the message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get the raw message text
        raw_message = ""
        if isinstance(data, dict):
            # If JSON, try to get a 'message' field, otherwise join all values
            raw_message = data.get('message', '\n'.join(str(v) for v in data.values()))
        else:
            raw_message = str(data)
        
        # Create formatted message
        message = "📊 <b>TradingView Alert</b>\n"
        message += "─────────────────────────\n"
        message += "─────────────────────────\n"
        message += "<b>Original Alert:</b>\n"
        message += f"<pre>{raw_message}</pre>"
        
        # Send to Telegram
        result = send_telegram_message(message)
        
        if result:
            print(f"✓ Alert sent to Telegram at {timestamp}")
            return jsonify({"status": "success", "message": "Alert sent"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to send"}), 500
            
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify the bot is working"""
    message = "✅ <b>Test Alert</b>\n\nYour TradingView webhook bot is working!"
    result = send_telegram_message(message)
    
    if result:
        return jsonify({"status": "success", "message": "Test message sent to Telegram"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to send test message"}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "running", "timestamp": datetime.now().isoformat()}), 200


@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "status": "online",
        "service": "TradingView to Telegram Bot",
        "endpoints": {
            "POST /webhook": "Receive TradingView alerts",
            "GET /test": "Send test message",
            "GET /health": "Health check"
        }
    }), 200


if __name__ == '__main__':
    print("=" * 50)
    print("TradingView to Telegram Bot Starting...")
    print("=" * 50)
    print(f"Telegram Bot Token: {TELEGRAM_BOT_TOKEN[:10]}..." if TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" else "⚠️  Please set your bot token!")
    print(f"Telegram Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"Port: {PORT}")
    print("=" * 50)
    print("\nServer will run on http://0.0.0.0:{PORT}")
    print("\nEndpoints:")
    print("  POST /webhook       - Receive TradingView alerts")
    print("  GET  /test          - Send test message to Telegram")
    print("  GET  /health        - Check if server is running")
    print("\n" + "=" * 50 + "\n")
    
    # Run the server
    app.run(host='0.0.0.0', port=PORT, debug=False)
