"""
Manual Topic Configuration Tool

Since GetForumTopicsRequest may not be available in older Telethon versions,
this script helps you manually configure topic IDs for forum groups.

Run this script, and it will:
1. List all your forum groups
2. Let you manually input topic IDs for each group
3. Save them to a config file that the bot can use
"""

import os
import toml
import asyncio
from telethon import TelegramClient
from telethon import functions, types

async def get_forum_groups():
    # Load config
    with open("assets/config.toml") as f:
        config = toml.loads(f.read())
    
    phone_number = config["telegram"]["phone_number"]
    api_id = config["telegram"]["api_id"]
    api_hash = config["telegram"]["api_hash"]
    
    client = TelegramClient(
        session="assets/sessions/%s" % (phone_number),
        api_id=api_id,
        api_hash=api_hash
    )
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print("ERROR: Not authorized. Please run main.py first to login.")
        await client.disconnect()
        return []
    
    user = await client.get_me()
    print(f"\n✓ Logged in as: @{user.username} ({user.first_name})\n")
    
    dialogs = await client.get_dialogs(limit=None)
    
    forum_groups = []
    for dialog in dialogs:
        if dialog.is_group:
            group_entity = dialog.entity
            if hasattr(group_entity, 'forum') and group_entity.forum:
                forum_groups.append({
                    'name': dialog.name,
                    'id': dialog.id,
                    'entity_id': group_entity.id
                })
    
    await client.disconnect()
    return forum_groups


def save_topic_config(groups_with_topics):
    """Save topic configuration to a file"""
    config = {}
    for group_name, topic_ids in groups_with_topics.items():
        config[group_name] = topic_ids
    
    config_path = "assets/manual_topics.toml"
    with open(config_path, "w") as f:
        f.write("# Manual Topic Configuration\n")
        f.write("# Format: \"Group Name\" = [topic_id1, topic_id2, ...]\n")
        f.write("# For FLIPS, you mentioned topic ID 1633576\n\n")
        f.write("[topics]\n")
        for group_name, topic_ids in config.items():
            if topic_ids:
                f.write(f'"{group_name}" = {topic_ids}\n')
    
    print(f"\n✓ Saved configuration to {config_path}")
    print("\nThe bot will now use these topic IDs when sending to these groups.")
    print("You can edit this file manually anytime to add/remove topics.")


async def main():
    print("="*80)
    print("Manual Topic Configuration Tool")
    print("="*80)
    print("\nThis tool helps you configure topic IDs for forum groups manually.")
    print("You'll need to find the topic IDs from Telegram.")
    print("\nTo find topic IDs:")
    print("1. Open the group in Telegram")
    print("2. Right-click on a message in a topic -> Copy Link")
    print("3. The topic ID is in the URL (the number after the last /)")
    print("   Example: t.me/c/1234567890/1633576 <- 1633576 is the topic ID")
    print()
    
    forum_groups = await get_forum_groups()
    
    if not forum_groups:
        print("No forum groups found.")
        return
    
    print(f"\nFound {len(forum_groups)} forum groups:\n")
    for i, group in enumerate(forum_groups, 1):
        print(f"{i}. {group['name']} (ID: {group['id']})")
    
    print("\n" + "="*80)
    print("Topic Configuration")
    print("="*80)
    print("\nFor each group, enter topic IDs separated by commas.")
    print("Press Enter to skip a group.")
    print("Example: 1633576, 1633577, 1633578")
    print()
    
    groups_with_topics = {}
    
    for group in forum_groups:
        group_name = group['name']
        print(f"\nGroup: {group_name}")
        
        # Auto-fill for FLIPS
        if "flip" in group_name.lower():
            default = "1633576"
            user_input = input(f"  Topic IDs (default: {default}): ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"  Topic IDs (comma-separated, or Enter to skip): ").strip()
        
        if user_input:
            try:
                topic_ids = [int(tid.strip()) for tid in user_input.split(",") if tid.strip()]
                if topic_ids:
                    groups_with_topics[group_name] = topic_ids
                    print(f"  ✓ Added {len(topic_ids)} topic(s)")
            except ValueError:
                print(f"  ⚠ Invalid input, skipping...")
        else:
            print(f"  ⏭ Skipped")
    
    if groups_with_topics:
        save_topic_config(groups_with_topics)
    else:
        print("\nNo topics configured.")

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()

