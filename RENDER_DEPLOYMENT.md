# Deploy TradingView Telegram Bot to Render.com

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Files

You'll need these 3 files (already created):
1. `tradingview_telegram_bot.py` - The main bot script
2. `requirements.txt` - Python dependencies
3. `render.yaml` - Render configuration (optional but recommended)

### Step 2: Create a GitHub Repository

1. Go to https://github.com and create a new repository
2. Name it something like `tradingview-telegram-bot`
3. Make it **Private** (recommended to keep your bot secure)
4. Upload all three files to the repository

**Quick Git commands if you have Git installed:**
```bash
git init
git add tradingview_telegram_bot.py requirements.txt render.yaml
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tradingview-telegram-bot.git
git push -u origin main
```

### Step 3: Sign Up for Render.com

1. Go to https://render.com
2. Sign up with your GitHub account (easiest way)
3. Authorize Render to access your repositories

### Step 4: Create a New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select your `tradingview-telegram-bot` repo
4. Render will auto-detect it's a Python app

**Configuration Settings:**
- **Name:** `tradingview-telegram-bot` (or any name you like)
- **Region:** Choose closest to you
- **Branch:** `main`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn tradingview_telegram_bot:app`
- **Instance Type:** **Free** (this is enough!)

### Step 5: Add Environment Variables

In the Render dashboard, scroll down to **Environment Variables** section and add:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather (e.g., `123456789:ABCdef...`) |
| `TELEGRAM_CHAT_ID` | Your chat ID (e.g., `123456789`) |
| `WEBHOOK_SECRET` | Any secret password (e.g., `mysecret123`) |

**Important:** Click the 🔒 lock icon next to each variable to keep them secret!

### Step 6: Deploy

1. Click **"Create Web Service"** at the bottom
2. Render will start building and deploying (takes 2-3 minutes)
3. Wait for the status to show **"Live"** with a green dot

### Step 7: Get Your Webhook URL

Once deployed, you'll see your app URL at the top, something like:
```
https://tradingview-telegram-bot-xxxx.onrender.com
```

Your webhook URL for TradingView will be:
```
https://tradingview-telegram-bot-xxxx.onrender.com/webhook?secret=YOUR_SECRET
```

Replace `YOUR_SECRET` with the secret you set in environment variables.

### Step 8: Test Your Bot

Visit this URL in your browser:
```
https://your-app-name.onrender.com/test
```

You should receive a test message in Telegram! ✅

### Step 9: Configure TradingView

In TradingView alert settings:
1. Check **"Webhook URL"**
2. Paste: `https://your-app-name.onrender.com/webhook?secret=YOUR_SECRET`
3. Set your alert message (JSON or plain text)
4. Save!

---

## Important Notes

### Free Tier Limitations

⚠️ **Render free tier has one limitation:**
- Your service will **spin down after 15 minutes of inactivity**
- It takes ~30 seconds to wake up when a webhook arrives
- **First alert after inactivity might be delayed**

**Solutions:**
1. **Accept the delay** (simplest, usually 30-40 seconds)
2. **Upgrade to paid tier** ($7/month for always-on)
3. **Use a ping service** to keep it awake (see below)

### Keeping Your Bot Awake (Optional)

If you want to avoid the spin-down, use a free cron job service to ping your bot every 10 minutes:

**Option 1: UptimeRobot** (Recommended)
1. Go to https://uptimerobot.com
2. Create a free account
3. Add a new monitor:
   - Type: HTTP(s)
   - URL: `https://your-app-name.onrender.com/health`
   - Interval: 5 minutes

**Option 2: Cron-Job.org**
1. Go to https://cron-job.org
2. Create a free account
3. Add a new cron job to hit your `/health` endpoint every 10 minutes

### Updating Your Bot

Whenever you push changes to GitHub, Render will automatically redeploy!

```bash
# Make changes to your code
git add .
git commit -m "Updated bot"
git push
```

Render will detect the push and redeploy automatically.

---

## Troubleshooting

### Bot not sending messages?
1. Check environment variables are set correctly in Render dashboard
2. View logs in Render: Dashboard → Your Service → Logs
3. Test the `/test` endpoint first

### TradingView webhook not working?
1. Make sure your webhook URL includes the secret parameter
2. Check Render logs for incoming requests
3. Verify the app is "Live" (green dot) in Render dashboard

### App keeps spinning down?
- This is normal for free tier
- Set up UptimeRobot to ping every 5-10 minutes
- Or upgrade to paid tier for always-on service

### Need to change settings?
- Edit environment variables in Render dashboard
- No need to redeploy, changes apply immediately

---

## Alternative: If You Don't Want to Use GitHub

If you don't want to use GitHub, you can deploy directly:

1. In Render, select **"Deploy from Git"**
2. Choose **"Public Git repository"**
3. Use a service like GitLab or Bitbucket
4. Or use Render's Blueprint feature with the `render.yaml` file

---

## Cost Summary

- **Render Free Tier:** ✅ Completely free forever
- **750 hours/month free** (more than enough for one service)
- **Automatic HTTPS** included
- **No credit card required** for free tier

That's it! Your bot will now run 24/7 in the cloud. 🚀
