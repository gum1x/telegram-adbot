import os
import toml
import asyncio
from telethon import TelegramClient
from telethon import functions, types, errors
from telethon.tl.types import InputReplyToMessage

async def test_forum_send():
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
    
    # Find a forum group (Jezzy Market or Unknown Market)
    dialogs = await client.get_dialogs(limit=None)
    
    test_group = None
    for dialog in dialogs:
        if dialog.is_group and ("jezzy" in dialog.name.lower() or "unknown market" in dialog.name.lower()):
            test_group = dialog
            break
    
    if not test_group:
        print("No test forum group found")
        return
    
    print(f"Testing with: {test_group.name}")
    group_entity = test_group.entity
    
    # Check if it's a forum
    if not hasattr(group_entity, 'forum') or not group_entity.forum:
        print("Group is not a forum group")
        return
    
    print(f"✓ Confirmed forum group\n")
    
    # Get topics
    try:
        result = await client(functions.channels.GetForumTopicsRequest(
            channel=group_entity,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=10
        ))
        
        topics = []
        for topic in result.topics:
            if hasattr(topic, 'id'):
                topic_title = getattr(topic, 'title', '')
                topics.append((topic.id, topic_title))
        
        print(f"Found {len(topics)} topics:")
        for topic_id, topic_title in topics:
            print(f"  - {topic_title or f'ID {topic_id}'} (ID: {topic_id})")
        
        if not topics:
            print("No topics found!")
            return
        
        # Test sending to first topic
        test_topic_id = topics[0][0]
        test_topic_title = topics[0][1] or f"ID {test_topic_id}"
        
        print(f"\n{'='*60}")
        print(f"Testing send to topic: {test_topic_title} (ID: {test_topic_id})")
        print(f"{'='*60}\n")
        
        # Get a test message from promotions channel
        print("Getting test message...")
        try:
            # Try to get message ID 13 from the promotions channel
            promo_channel_id = -1002684204333
            promo_channel = await client.get_entity(promo_channel_id)
            test_message = await client.get_messages(promo_channel, ids=13)
            
            if not test_message:
                print("Could not get test message ID 13")
                return
            
            print(f"✓ Got test message: {test_message.id}\n")
            
        except Exception as e:
            print(f"Error getting test message: {e}")
            return
        
        # Test Method 1: InputReplyToMessage with top_msg_id
        print("Method 1: InputReplyToMessage with top_msg_id")
        try:
            reply_header = InputReplyToMessage(
                reply_to_msg_id=0,
                top_msg_id=test_topic_id
            )
            sent = await client.forward_messages(
                group_entity,
                test_message,
                reply_to=reply_header
            )
            print(f"  ✓ SUCCESS! Sent message ID: {sent[0].id if isinstance(sent, list) else sent.id}")
        except Exception as e:
            print(f"  ✗ FAILED: {type(e).__name__}: {str(e)}")
        
        # Test Method 2: Direct topic_id as reply_to
        print("\nMethod 2: topic_id directly as reply_to")
        try:
            sent = await client.forward_messages(
                group_entity,
                test_message,
                reply_to=test_topic_id
            )
            print(f"  ✓ SUCCESS! Sent message ID: {sent[0].id if isinstance(sent, list) else sent.id}")
        except Exception as e:
            print(f"  ✗ FAILED: {type(e).__name__}: {str(e)}")
        
        # Test Method 3: send_message if text
        if hasattr(test_message, 'text') and test_message.text:
            print("\nMethod 3: send_message with topic_id")
            try:
                sent = await client.send_message(
                    group_entity,
                    test_message.text[:100] + "...",  # Truncate for test
                    reply_to=test_topic_id
                )
                print(f"  ✓ SUCCESS! Sent message ID: {sent.id}")
            except Exception as e:
                print(f"  ✗ FAILED: {type(e).__name__}: {str(e)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_forum_send())

