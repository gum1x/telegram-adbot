# Deploying to Render.com

## Step-by-Step Deployment Guide

### Step 1: Push Your Code to GitHub/GitLab

**First, you need to push your code to a Git repository:**

1. **Initialize Git** (if not already done):
   ```bash
   cd /Users/0x/Telegram-Marketplace-Advertiser-and-groups-1
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create a GitHub repository**:
   - Go to https://github.com/new
   - Create a new repository (make it private if you want)
   - Don't initialize with README

3. **Push your code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

**⚠️ Important**: Your `config.toml` is in `.gitignore`, so it WON'T be pushed to GitHub. This is good for security, but we need to handle it separately.

### Step 2: Deploy to Render

**⚠️ IMPORTANT: Free Tier Limitations**
- Free instances **spin down after 15 minutes of inactivity**
- **No persistent disk** - session files may be lost on restart
- **Solution**: Use a free ping service (see below) OR upgrade to paid ($7/month)

1. **Go to Render.com** and sign up/login
2. **Click "New +"** → **"Web Service"** (NOT Background Worker - Web Service has free tier)
3. **Connect your repository**:
   - Click "Connect account" if you haven't already
   - Authorize Render to access your GitHub/GitLab
   - Select your repository
   - Select the branch (usually `main`)

4. **Configure the service**:
   - **Name**: `telegram-adbot` (or whatever you want)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `Adbot` (important! Your code is in the Adbot folder)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 main.py`
   - **Instance Type**: **Free** (or Starter $7/month for persistent disk)

5. **Add Environment Variables** (click "Advanced"):
   - `PYTHONUNBUFFERED` = `1` (for real-time logs)

### Step 3: Add Your Config File

Since `config.toml` isn't in Git, you have **two options**:

#### Option A: Use Render's Shell (Recommended)

1. After deployment starts, go to your service on Render
2. Click **"Shell"** tab
3. Run these commands:
   ```bash
   cd Adbot
   cp assets/config.toml.example assets/config.toml
   nano assets/config.toml
   ```
4. Paste your config content (copy from your local `config.toml`)
5. Save and exit (Ctrl+X, then Y, then Enter)

#### Option B: Temporarily Include Config in Git

1. **Temporarily remove from .gitignore**:
   ```bash
   # Edit .gitignore and comment out or remove:
   # assets/config.toml
   ```

2. **Add and commit**:
   ```bash
   git add Adbot/assets/config.toml
   git commit -m "Add config for Render deployment"
   git push
   ```

3. **After deployment, remove it again**:
   ```bash
   git rm --cached Adbot/assets/config.toml
   git commit -m "Remove config from git"
   git push
   ```

### Step 4: First Authentication

1. **Check Render logs** - the bot will ask for a verification code
2. **Get the code from Telegram** (check your Telegram app)
3. **Enter it in Render Shell** or check logs for the prompt
4. **If you have 2FA**, you'll need to enter your password too

After first authentication, the session file will be saved and it will run automatically!

### Step 5: Keep Free Tier Alive (IMPORTANT!)

**Free tier spins down after 15 minutes of inactivity!** You need to ping it regularly:

#### Option A: Use Free Ping Service (Recommended)

1. **Get your Render URL**: After deployment, Render gives you a URL like `https://telegram-adbot.onrender.com`

2. **Set up UptimeRobot** (free):
   - Go to https://uptimerobot.com (free account)
   - Add a new monitor
   - **Type**: HTTP(s)
   - **URL**: `https://your-app.onrender.com/health`
   - **Interval**: 5 minutes
   - Save

3. **Alternative**: Use cron-job.org or similar free services to ping your URL every 5 minutes

#### Option B: Upgrade to Starter ($7/month)

- **Persistent disk** - session files survive restarts
- **No spin-down** - stays running 24/7
- **Better reliability** for production use

## Your Config Settings

Make sure your `config.toml` on Render has:
```toml
[telegram]
auto_run=true
source_chat_id=-1002684204333
message_id=13
skip_join_groups=true

[group_topics]
"-1002256623070"=12018
```

## Monitoring

- **Logs**: Click "Logs" tab in Render to see real-time output
- **Restarts**: Render will auto-restart if the bot crashes
- **Updates**: Push to GitHub and Render will auto-deploy

## Troubleshooting

- **"Config file not found"**: Make sure `config.toml` exists in `Adbot/assets/`
- **"Session file error"**: This is normal on first run - you'll authenticate once
- **"Module not found"**: Check that `requirements.txt` is in the `Adbot` folder
- **Bot stops working**: Free tier spun down - set up ping service (UptimeRobot) or upgrade to paid
- **Session lost on restart**: Free tier has no persistent disk - upgrade to Starter ($7/month) for persistent storage

