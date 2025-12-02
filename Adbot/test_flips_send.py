import os
import toml
import asyncio
from telethon import TelegramClient
from telethon import functions, types, errors

async def test_flips():
    # Load config
    with open("assets/config.toml") as f:
        config = toml.loads(f.read())
    
    phone_number = config["telegram"]["phone_number"]
    api_id = config["telegram"]["api_id"]
    api_hash = config["telegram"]["api_hash"]
    
    # Get exclusion list
    excluded_names = config.get("filters", {}).get("excluded_names", "")
    excluded_list = [name.strip().lower() for name in excluded_names.split(",") if name.strip()]
    
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
    
    print("="*80)
    print("Testing FLIPS group...")
    print("="*80)
    
    flips_group = None
    for dialog in dialogs:
        if dialog.is_group and "flip" in dialog.name.lower():
            flips_group = dialog
            break
    
    if not flips_group:
        print("\n✗ FLIPS group not found!")
        return
    
    print(f"\n✓ Found: {flips_group.name}")
    print(f"  ID: {dialog.id}")
    
    # Check if excluded
    group_name_lower = flips_group.name.lower()
    is_blocked = False
    for excluded_name in excluded_list:
        if excluded_name in group_name_lower:
            is_blocked = True
            print(f"  🚫 BLOCKED by filter: '{excluded_name}'")
            break
    
    if is_blocked:
        print("\n❌ FLIPS is being blocked by exclusion filter!")
        print("   Remove it from excluded_names in config.toml")
        return
    
    print(f"  ✅ Not blocked - should receive messages")
    
    # Check if it's a forum group
    group_entity = flips_group.entity
    is_forum = hasattr(group_entity, 'forum') and group_entity.forum
    
    print(f"  Forum group: {is_forum}")
    
    if is_forum:
        # Get topics
        try:
            result = await client(functions.channels.GetForumTopicsRequest(
                channel=group_entity,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100
            ))
            topics = []
            for topic in result.topics:
                if hasattr(topic, 'id'):
                    topic_title = getattr(topic, 'title', '')
                    topics.append((topic.id, topic_title))
            
            print(f"  Topics found: {len(topics)}")
            if topics:
                print("  Topic list:")
                for topic_id, topic_title in topics[:10]:
                    print(f"    - {topic_title or f'ID {topic_id}'} (ID: {topic_id})")
        except Exception as e:
            print(f"  Error getting topics: {e}")
    
    # Check last message
    try:
        last_messages = await client.get_messages(flips_group.entity, limit=3)
        print(f"\n  Last 3 messages:")
        for msg in last_messages:
            sender = "You" if (msg.from_id and hasattr(msg.from_id, 'user_id') and msg.from_id.user_id == user.id) else "Other"
            print(f"    - {sender}: {msg.id} ({msg.date})")
    except Exception as e:
        print(f"  Error getting messages: {e}")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_flips())

