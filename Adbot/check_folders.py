import os
import toml
import asyncio
from telethon import TelegramClient

async def check_folders():
    # Load config
    with open("assets/config.toml") as f:
        config = toml.loads(f.read())
    
    phone_number = config["telegram"]["phone_number"]
    api_id = config["telegram"]["api_id"]
    api_hash = config["telegram"]["api_hash"]
    
    # Create client
    client = TelegramClient(
        session="assets/sessions/%s" % (phone_number),
        api_id=api_id,
        api_hash=api_hash
    )
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Not authorized. Please run main.py first to login.")
        return
    
    user = await client.get_me()
    print(f"\n✓ Logged in as: @{user.username} ({user.first_name})\n")
    
    # Get all dialogs
    dialogs = await client.get_dialogs(limit=None)
    
    print("="*80)
    print("Checking for folder-based groups...")
    print("="*80)
    
    # Count groups by type
    regular_groups = []
    supergroups = []
    channels = []
    
    for dialog in dialogs:
        if dialog.is_group:
            if hasattr(dialog.entity, 'megagroup') and dialog.entity.megagroup:
                supergroups.append(dialog)
            else:
                regular_groups.append(dialog)
        elif dialog.is_channel and not dialog.is_group:
            channels.append(dialog)
    
    print(f"\nTotal chats found: {len(dialogs)}")
    print(f"  • Regular groups: {len(regular_groups)}")
    print(f"  • Supergroups (typically from folders): {len(supergroups)}")
    print(f"  • Channels: {len(channels)}")
    
    print(f"\nGroups that will be targeted by bot: {len(regular_groups) + len(supergroups)}")
    
    # Show some folder group examples
    if supergroups:
        print(f"\n📁 Sample of supergroups (likely from folders):")
        for i, group in enumerate(supergroups[:10], 1):
            member_count = getattr(group.entity, 'participants_count', 'N/A')
            username = f"@{group.entity.username}" if hasattr(group.entity, 'username') and group.entity.username else "Private"
            print(f"  {i}. {group.name} - {username} ({member_count} members)")
        
        if len(supergroups) > 10:
            print(f"  ... and {len(supergroups) - 10} more supergroups")
    
    # Check if the bot's get_groups() would find them
    print("\n" + "="*80)
    print("Verifying bot's group detection...")
    print("="*80)
    
    bot_groups = []
    for dialog in dialogs:
        if dialog.is_group and dialog.is_channel:  # This is what the bot checks
            bot_groups.append(dialog)
    
    print(f"\n✓ Bot will target {len(bot_groups)} groups")
    
    if len(bot_groups) != len(supergroups) + len(regular_groups):
        print(f"⚠ Warning: There's a mismatch!")
        print(f"  Expected: {len(supergroups) + len(regular_groups)}")
        print(f"  Bot will find: {len(bot_groups)}")
    else:
        print(f"✓ All groups will be detected correctly!")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(check_folders())

