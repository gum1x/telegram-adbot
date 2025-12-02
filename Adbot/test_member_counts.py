import os
import toml
import asyncio
from telethon import TelegramClient
from telethon import functions

async def test_member_counts():
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
        print("Not authorized.")
        return
    
    user = await client.get_me()
    print(f"\n✓ Logged in as: @{user.username}\n")
    
    # Get all dialogs
    dialogs = await client.get_dialogs(limit=None)
    
    print("Testing member count detection methods:\n")
    print("="*100)
    
    groups_tested = 0
    for dialog in dialogs:
        if dialog.is_group and groups_tested < 10:
            groups_tested += 1
            
            # Method 1: From dialog entity
            count1 = getattr(dialog.entity, 'participants_count', None)
            
            # Method 2: Try to get full channel info
            count2 = None
            try:
                if hasattr(dialog.entity, 'id'):
                    full = await client(functions.channels.GetFullChannelRequest(channel=dialog.entity))
                    count2 = full.full_chat.participants_count
            except Exception as e:
                count2 = f"Error: {type(e).__name__}"
            
            print(f"\n{groups_tested}. {dialog.name}")
            print(f"   Method 1 (entity.participants_count): {count1}")
            print(f"   Method 2 (GetFullChannelRequest): {count2}")
            print(f"   Match: {'✓' if count1 == count2 else '✗'}")
    
    print("\n" + "="*100)
    print("\nConclusion:")
    print("- Method 1 is faster but may show 0 or None for some groups")
    print("- Method 2 is more accurate but requires an API call per group (slower)")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_member_counts())

