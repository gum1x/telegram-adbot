# Adbot Telegram

A powerful Telegram bot for automatically forwarding messages from a channel/group to multiple marketplace groups with advanced filtering and forum topic support.

## Features

- 🔄 Forward messages from any channel or group to multiple target groups
- 🎯 Smart filtering by group size (min/max members)
- 🚫 Exclude specific groups by name
- 🎲 Random topic selection for forum-enabled groups
- ⏱️ Configurable send intervals and loop timing
- 🔐 2FA (Two-Factor Authentication) support
- 📊 Real-time group scanning and selection
- ✅ Skip groups where your message is already the latest

## Requirements

- Python 3.7+
- Telegram API credentials (API ID and Hash from https://my.telegram.org/auth)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Adbot
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Configure your credentials:
```bash
cp assets/config.toml.example assets/config.toml
```

4. Edit `assets/config.toml` with your credentials:
   - Add your phone number
   - Add your API ID and API Hash from https://my.telegram.org/auth
   - Adjust filters and sending intervals as needed

## Configuration

### Telegram Settings
```toml
[telegram]
phone_number="+1234567890"
api_id=12345678
api_hash="your_api_hash_here"
```

### Sending Settings
```toml
[sending]
send_interval=0      # Seconds to wait between each message
loop_interval=3600   # Seconds to wait before re-sending to all groups
```

### Filters
```toml
[filters]
min_members=50       # Minimum group members (set to 0 to disable)
max_members=15000    # Maximum group members
excluded_names="ogu chat,chatter"  # Comma-separated list of excluded group names
```

## Usage

### List Your Groups
```bash
python3 list_my_groups.py
```

### Export Your Groups
```bash
python3 export_my_groups.py
```

### Run the Bot
```bash
python3 main.py
```

The bot will:
1. Ask if you want to join groups from a list (optional)
2. Display all your groups and channels
3. Prompt you to select the source group/channel
4. Show messages from that source
5. Ask which message to forward
6. Start forwarding to all eligible groups

## How It Works

1. **Real-time Group Detection**: Fetches all groups you're currently in
2. **Smart Filtering**: Applies size and name filters to skip unwanted groups
3. **Forum Support**: Automatically detects forum-enabled groups and randomly selects topics
4. **Anti-Spam**: Skips groups where your message is already the latest
5. **Rate Limiting**: Respects Telegram's rate limits with automatic retry

## Features in Detail

### Forum Topic Support
For groups with topics/sections enabled, the bot will:
- Automatically detect available topics
- Randomly select a topic for each message
- Log which topic was selected

### Filters
- **Size Filters**: Only send to groups within your specified member range
- **Name Filters**: Exclude specific groups by keywords in their name (case-insensitive)
- **Latest Message Check**: Skip groups where you already sent the latest message

### 2FA Support
The bot supports Telegram accounts with Two-Factor Authentication enabled. It will prompt for your password when needed.

## Utilities

### `list_my_groups.py`
Lists all groups you're currently in with details:
- Group name
- Username/link
- Member count
- Group ID

### `export_my_groups.py`
Exports all your groups to `assets/groups.txt` for backup or reference.

## Security Notes

- Never commit your `config.toml` file with real credentials
- Session files are stored locally and contain authentication data
- Keep your API credentials secure
- The `.gitignore` is configured to exclude sensitive files

## Troubleshooting

### "Database is locked" error
- Close any other instances of the bot
- Wait a few seconds and try again

### "UPDATE_APP_TO_LOGIN" error
- Update Telethon: `pip3 install --upgrade Telethon`

### Messages not sending to forum topics
- Ensure you have permission to post in those topics
- Check that the group has topics enabled

## License

This project is for educational purposes only. Use responsibly and comply with Telegram's Terms of Service.

## Disclaimer

This bot is provided as-is. The authors are not responsible for any misuse or violations of Telegram's Terms of Service. Always respect group rules and avoid spam.


