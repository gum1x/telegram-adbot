# Deploying to Railway.app

## Why Railway?

✅ **Better than Render for bots:**
- **Persistent storage** - Session files survive restarts (even on free tier!)
- **No spin-down** - Stays running 24/7
- **Better free tier** - $1/month credit (after 30-day $5 trial)
- **Pay-as-you-go** - Only pay for what you use

## Pricing Estimate

### Free Tier (After Trial)
- **$1/month credit** included
- **0.5 GB RAM**, 1 vCPU per service
- **0.5 GB storage**

**Estimated monthly cost for Telegram bot:**
- Memory (0.5 GB): ~$5/month
- CPU (0.1 vCPU): ~$2/month  
- Storage: ~$0.10/month
- **Total: ~$7/month**
- **With $1 credit: ~$6/month actual cost**

### Hobby Plan ($5/month)
- **$5/month credit** included
- Up to 8 GB RAM, 8 vCPU
- More storage

**Estimated monthly cost:**
- Same usage as above (~$7/month)
- **With $5 credit: ~$2/month actual cost** 🎉

**Recommendation: Start with Free tier, upgrade to Hobby ($5/month) if needed**

## Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

Your code is already on GitHub at: `https://github.com/gum1x/telegram-adbot`

### Step 2: Deploy on Railway

1. **Go to Railway.app** and sign up/login
   - Use GitHub to sign in (easiest)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `gum1x/telegram-adbot`

3. **Configure Service**
   - Railway will auto-detect Python
   - **Root Directory**: Set to `Adbot` (important!)
   - **Start Command**: `python3 main.py` (auto-detected)
   - Railway will automatically:
     - Install dependencies from `requirements.txt`
     - Run your bot

4. **Add Environment Variables** (if needed):
   - `PYTHONUNBUFFERED=1` (for better logs)

### Step 3: Add Your Config File

Since `config.toml` isn't in Git, add it via Railway:

1. Go to your service → **Variables** tab
2. Click **"Add Variable"**
3. Or use **Railway CLI**:
   ```bash
   railway login
   railway link
   railway variables set CONFIG_TOML="$(cat Adbot/assets/config.toml)"
   ```

**Better Option**: Use Railway's file system:
1. Go to your service → **Data** tab
2. Click **"Mount Volume"**
3. Navigate to `Adbot/assets/`
4. Create `config.toml` with your settings

### Step 4: First Authentication

1. **Check Railway logs** - the bot will ask for verification code
2. **Get code from Telegram** (check your Telegram app)
3. **Enter code** - Railway logs will show the prompt
4. **If 2FA**: Enter password when prompted

After authentication, session files will be saved in `assets/sessions/` and persist!

## Your Config Settings

Make sure your `config.toml` has:
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

- **Logs**: Real-time logs in Railway dashboard
- **Metrics**: CPU, Memory, Network usage
- **Costs**: Track spending in dashboard
- **Restarts**: Auto-restarts on failure

## Cost Optimization Tips

1. **Start with Free tier** - Monitor usage for first month
2. **Set resource limits** - Railway allows you to cap resources
3. **Upgrade to Hobby** - If usage exceeds $1/month, Hobby plan ($5) gives $5 credit
4. **Monitor usage** - Railway dashboard shows real-time costs

## Advantages Over Render

✅ **Persistent storage** - Session files survive restarts  
✅ **No spin-down** - Runs 24/7 without ping services  
✅ **Better pricing** - Pay only for what you use  
✅ **Easier deployment** - Auto-detects everything  
✅ **Better free tier** - More generous than Render  

## Troubleshooting

- **"Config file not found"**: Add `config.toml` via Railway file system or variables
- **"Session file error"**: Normal on first run - authenticate once
- **High costs**: Check resource usage, consider setting limits
- **Bot stops**: Check logs, Railway auto-restarts on failure

## Next Steps

1. Deploy on Railway (takes ~2 minutes)
2. Add your `config.toml` file
3. Authenticate via Telegram
4. Monitor costs for first week
5. Upgrade to Hobby plan if needed ($5/month)

**Estimated total cost: $0-6/month** (depending on usage and plan)

