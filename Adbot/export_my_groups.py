import os
import toml
import asyncio
from telethon import TelegramClient

async def export_groups():
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
    print(f"\n✓ Logged in as: @{user.username} ({user.first_name})")
    
    # Get all dialogs (chats)
    dialogs = await client.get_dialogs(limit=None)
    
    # Filter for groups and supergroups
    groups = []
    group_links = []
    
    for dialog in dialogs:
        if dialog.is_group:
            groups.append(dialog)
            # Get username or use chat ID for private groups
            if hasattr(dialog.entity, 'username') and dialog.entity.username:
                group_links.append(f"https://t.me/{dialog.entity.username}")
            else:
                # For private groups, we'll use the chat ID (bot can still access them if already joined)
                group_links.append(f"{dialog.id}")
    
    print(f"\n✓ Found {len(groups)} groups")
    
    # Write to groups.txt
    with open("assets/groups.txt", "w", encoding="utf-8") as f:
        for link in group_links:
            f.write(link + "\n")
    
    print(f"✓ Exported {len(group_links)} groups to assets/groups.txt")
    print(f"\nYour bot will now forward messages to all {len(group_links)} groups you're in!")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(export_groups())


