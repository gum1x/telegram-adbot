import os
import toml
import asyncio
from telethon import TelegramClient
from telethon import functions, types, errors

async def list_groups_with_topics():
    print("Loading configuration...")
    # Load config
    with open("assets/config.toml") as f:
        config = toml.loads(f.read())
    
    phone_number = config["telegram"]["phone_number"]
    api_id = config["telegram"]["api_id"]
    api_hash = config["telegram"]["api_hash"]
    
    print(f"Creating client for {phone_number}...")
    # Create client
    client = TelegramClient(
        session="assets/sessions/%s" % (phone_number),
        api_id=api_id,
        api_hash=api_hash
    )
    
    print("Connecting to Telegram...")
    await client.connect()
    
    if not await client.is_user_authorized():
        print("ERROR: Not authorized. Please run main.py first to login.")
        await client.disconnect()
        return
    
    user = await client.get_me()
    print(f"\n✓ Logged in as: @{user.username} ({user.first_name})\n")
    
    # Get all dialogs
    print("Fetching all dialogs...")
    dialogs = await client.get_dialogs(limit=None)
    
    print("="*80)
    print("Groups with Discussion Sections (Forum Topics)")
    print("="*80)
    print()
    
    forum_groups = []
    
    for dialog in dialogs:
        if dialog.is_group:
            group_entity = dialog.entity
            
            # Check if it's a forum group
            if hasattr(group_entity, 'forum') and group_entity.forum:
                try:
                    print(f"📁 Checking: {dialog.name}...", end=" ")
                    
                    # Try different methods to get topics
                    topics = []
                    
                    # Method 1: Try GetForumTopicsRequest (newer Telethon versions)
                    try:
                        if hasattr(functions.channels, 'GetForumTopicsRequest'):
                            result = await client(functions.channels.GetForumTopicsRequest(
                                channel=group_entity,
                                offset_date=0,
                                offset_id=0,
                                offset_topic=0,
                                limit=100
                            ))
                            
                            for topic in result.topics:
                                if hasattr(topic, 'id'):
                                    topic_title = getattr(topic, 'title', '')
                                    topics.append((topic.id, topic_title))
                    except (AttributeError, TypeError):
                        # Method not available in this Telethon version
                        pass
                    except Exception:
                        pass
                    
                    # Method 2: If Method 1 didn't work, extract from messages
                    if not topics:
                        print("(extracting from messages)", end=" ")
                        topics = await extract_topics_from_messages(client, group_entity)
                    
                    if topics:
                        forum_groups.append({
                            'name': dialog.name,
                            'id': dialog.id,
                            'entity_id': group_entity.id,
                            'topics': topics
                        })
                        
                        print(f"✓ Found {len(topics)} topics")
                        
                        print(f"\n   📁 {dialog.name}")
                        print(f"   Group ID: {dialog.id}")
                        print(f"   Entity ID: {group_entity.id}")
                        print(f"   Topics ({len(topics)}):")
                        
                        # Check for preferred topics
                        has_other = False
                        has_insta = False
                        
                        for topic_id, topic_title in topics:
                            marker = ""
                            if topic_title:
                                title_lower = topic_title.lower()
                                if 'other' in title_lower:
                                    marker = " ⭐ (other)"
                                    has_other = True
                                elif 'insta' in title_lower:
                                    marker = " ⭐ (insta)"
                                    has_insta = True
                            
                            print(f"      • {topic_title or f'ID {topic_id}'} (ID: {topic_id}){marker}")
                        
                        if has_other:
                            print(f"   → Will use 'other' topic")
                        elif has_insta:
                            print(f"   → Will use 'insta' topic")
                        else:
                            print(f"   → Will use random topic")
                        
                        print()
                    else:
                        print("No topics found")
                        
                except Exception as e:
                    print(f"Error: {str(e)}")
                    print()
    
    print("="*80)
    print(f"Total forum groups found: {len(forum_groups)}")
    print("="*80)
    
    # Check for FLIPS specifically
    print("\n" + "="*80)
    print("FLIPS Group Details:")
    print("="*80)
    
    flips_found = False
    for group_info in forum_groups:
        if "flip" in group_info['name'].lower():
            flips_found = True
            print(f"\n✓ Found: {group_info['name']}")
            print(f"  Group ID: {group_info['id']}")
            print(f"  Entity ID: {group_info['entity_id']}")
            print(f"  Topics:")
            for topic_id, topic_title in group_info['topics']:
                marker = " ⭐ TARGET" if topic_id == 1633576 else ""
                print(f"    - {topic_title or f'ID {topic_id}'} (ID: {topic_id}){marker}")
            
            # Check if topic 1633576 exists
            topic_1633576 = [t for t in group_info['topics'] if t[0] == 1633576]
            if topic_1633576:
                print(f"\n  ✅ Topic ID 1633576 found: '{topic_1633576[0][1] or 'No title'}'")
            else:
                print(f"\n  ⚠ Topic ID 1633576 NOT found in this group!")
                print(f"  Available topic IDs: {[t[0] for t in group_info['topics']]}")
            break
    
    if not flips_found:
        print("\n✗ FLIPS group not found or doesn't have forum topics")
    
    print("\n" + "="*80)
    print("Done!")
    print("="*80)
    
    await client.disconnect()


async def extract_topics_from_messages(client, group_entity):
    """Extract topic IDs from messages in the group by checking reply_to.top_msg_id"""
    topics_dict = {}
    
    try:
        # Get recent messages to extract topic IDs
        messages = await client.get_messages(group_entity, limit=500)
        
        for msg in messages:
            if hasattr(msg, 'reply_to') and msg.reply_to:
                if hasattr(msg.reply_to, 'top_msg_id') and msg.reply_to.top_msg_id:
                    topic_id = msg.reply_to.top_msg_id
                    # Try to get topic title from the topic message itself
                    if topic_id not in topics_dict:
                        try:
                            # Get the topic message to extract title
                            topic_msg = await client.get_messages(group_entity, ids=topic_id)
                            if topic_msg and hasattr(topic_msg, 'message') and topic_msg.message:
                                # Topic title is usually in the first message of the topic
                                topics_dict[topic_id] = topic_msg.message[:50]  # First 50 chars
                            else:
                                topics_dict[topic_id] = ''
                        except:
                            topics_dict[topic_id] = ''
    except Exception as e:
        print(f"(extraction error: {str(e)[:30]})")
    
    # Convert to list of tuples
    return [(topic_id, title) for topic_id, title in topics_dict.items()]


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(list_groups_with_topics())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
