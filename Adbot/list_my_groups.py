import os
import toml
import asyncio
from telethon import TelegramClient

async def list_groups():
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
    
    # Get all dialogs (chats)
    dialogs = await client.get_dialogs(limit=None)
    
    # Filter for groups and supergroups
    groups = []
    for dialog in dialogs:
        if dialog.is_group:
            groups.append(dialog)
    
    print(f"Total groups you're in: {len(groups)}\n")
    print("=" * 80)
    
    for i, group in enumerate(groups, 1):
        # Get group username/invite link if available
        username = f"@{group.entity.username}" if hasattr(group.entity, 'username') and group.entity.username else "Private Group"
        print(f"{i}. {group.name}")
        print(f"   Link: {username}")
        print(f"   ID: {group.id}")
        print(f"   Members: {getattr(group.entity, 'participants_count', 'N/A')}")
        print()
    
    print("=" * 80)
    print(f"\nTotal: {len(groups)} groups")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(list_groups())

