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
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID",   "YOUR_CHAT_ID_HERE")
WEBHOOK_SECRET     = os.environ.get("WEBHOOK_SECRET",     "your_secret_key_here")
PORT               = int(os.environ.get("PORT", 5000))
# =========================================


def send_telegram_message(message):
    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return None


def extract_message(req):
    """
    TradingView alert() sends the text as a raw UTF-8 body
    with NO Content-Type header (or text/plain).
    We must read raw bytes and decode manually.
    """

    # 1. Raw bytes -> string (most reliable for TradingView alert())
    raw_bytes = req.get_data()          # always works, returns bytes
    if raw_bytes:
        try:
            text = raw_bytes.decode("utf-8").strip()
            if text:
                # Try JSON first (some setups wrap in JSON)
                if text.startswith("{"):
                    try:
                        data = json.loads(text)
                        for key in ("message", "text", "alert", "msg", "content"):
                            if key in data and str(data[key]).strip():
                                return str(data[key]).strip()
                        parts = [str(v) for v in data.values() if str(v).strip()]
                        if parts:
                            return "\n".join(parts)
                    except json.JSONDecodeError:
                        pass
                # Plain text - return as-is
                return text
        except Exception:
            pass

    # 2. Form data fallback
    form = req.form.to_dict()
    if form:
        for key in ("message", "text", "alert", "msg", "content"):
            if key in form and form[key].strip():
                return form[key].strip()
        parts = [str(v) for v in form.values() if str(v).strip()]
        if parts:
            return "\n".join(parts)

    return "(No alert content received)"


def format_alert(raw_message: str, timestamp: str) -> str:
    """
    Build a nicely formatted Telegram HTML message.
    The Pine Script already sends lines like:
        YELLOW BAR - NIFTY
        Timeframe : 5
        Bar High  : 24500
    So we just wrap it cleanly.
    """
    lines = raw_message.splitlines()

    # First line is usually the signal title
    title = lines[0].strip() if lines else "TradingView Alert"
    body  = "\n".join(l for l in lines[1:] if l.strip())

    msg  = f"<b>{title}</b>\n"
    msg += "─────────────────────────\n"
    msg += f"Time: {timestamp}\n"
    if body:
        msg += "─────────────────────────\n"
        msg += f"<pre>{body}</pre>"
    return msg


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Optional secret check
        secret = request.args.get('secret', '')
        if WEBHOOK_SECRET and secret != WEBHOOK_SECRET:
            return jsonify({"status": "error", "message": "Invalid secret"}), 403

        timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        raw_message = extract_message(request)

        print(f"[{timestamp}] Raw payload ({len(raw_message)} chars):\n{raw_message[:300]}")

        message = format_alert(raw_message, timestamp)
        result  = send_telegram_message(message)

        if result and result.get("ok"):
            print(f"Alert sent at {timestamp}")
            return jsonify({"status": "success"}), 200
        else:
            print(f"Telegram error: {result}")
            return jsonify({"status": "error", "telegram_response": result}), 500

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/test', methods=['GET'])
def test():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sample = (
        "YELLOW BAR - NIFTY\n"
        "Timeframe : 5\n"
        "Bar High  : 24500.00\n"
        "Bar Low   : 24450.00\n"
        "Volume    : 123456"
    )
    message = format_alert(sample, timestamp)
    result  = send_telegram_message(message)
    if result and result.get("ok"):
        return jsonify({"status": "success", "message": "Test sent"}), 200
    return jsonify({"status": "error", "detail": result}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "timestamp": datetime.now().isoformat()}), 200


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "service": "TradingView to Telegram Bot",
        "endpoints": {
            "POST /webhook": "Receive TradingView alerts",
            "GET /test":     "Send test message",
            "GET /health":   "Health check"
        }
    }), 200


if __name__ == '__main__':
    print("=" * 50)
    print("TradingView to Telegram Bot Starting...")
    print(f"Token  : {TELEGRAM_BOT_TOKEN[:10]}..." if TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" else "Set TELEGRAM_BOT_TOKEN!")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"Port   : {PORT}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=PORT, debug=False)
