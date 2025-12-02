import os
import toml
import asyncio
from telethon import TelegramClient

async def check_flips():
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
    
    # Get all dialogs
    dialogs = await client.get_dialogs(limit=None)
    
    print("\n" + "="*80)
    print("Checking for FLIPS group...")
    print("="*80)
    
    flips_found = False
    for dialog in dialogs:
        if dialog.is_group:
            group_name = dialog.name
            group_name_lower = group_name.lower()
            
            # Check if it's FLIPS
            if "flip" in group_name_lower:
                flips_found = True
                print(f"\n✓ Found: {group_name}")
                print(f"  ID: {dialog.id}")
                
                # Check if it would be blocked
                is_blocked = False
                matched_filter = None
                for excluded_name in excluded_list:
                    if excluded_name in group_name_lower:
                        is_blocked = True
                        matched_filter = excluded_name
                        break
                
                if is_blocked:
                    print(f"  Status: 🚫 BLOCKED (matched filter: '{matched_filter}')")
                    print(f"  Result: Will NOT receive messages")
                else:
                    print(f"  Status: ✅ ALLOWED")
                    print(f"  Result: WILL receive messages")
                
                # Check member count
                member_count = getattr(dialog.entity, 'participants_count', 'N/A')
                print(f"  Members: {member_count}")
                break
    
    if not flips_found:
        print("\n✗ No group containing 'flip' found")
    
    # Show all groups that will be targeted
    print("\n" + "="*80)
    print("All groups that WILL receive messages (sample):")
    print("="*80)
    
    targeted = []
    for dialog in dialogs:
        if dialog.is_group:
            group_name_lower = dialog.name.lower()
            is_blocked = False
            
            for excluded_name in excluded_list:
                if excluded_name in group_name_lower:
                    is_blocked = True
                    break
            
            if not is_blocked:
                targeted.append(dialog.name)
    
    print(f"\nTotal groups that will receive messages: {len(targeted)}")
    print("\nFirst 20 groups:")
    for i, name in enumerate(targeted[:20], 1):
        print(f"  {i}. {name}")
    
    if len(targeted) > 20:
        print(f"  ... and {len(targeted) - 20} more")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(check_flips())

