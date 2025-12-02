import os
import toml
import asyncio
from telethon import TelegramClient

async def verify_exclusions():
    # Load config
    with open("assets/config.toml") as f:
        config = toml.loads(f.read())
    
    phone_number = config["telegram"]["phone_number"]
    api_id = config["telegram"]["api_id"]
    api_hash = config["telegram"]["api_hash"]
    
    # Get exclusion list
    excluded_names = config.get("filters", {}).get("excluded_names", "")
    excluded_list = [name.strip().lower() for name in excluded_names.split(",") if name.strip()]
    
    print("\n" + "="*80)
    print("EXCLUSION LIST VERIFICATION")
    print("="*80)
    print(f"\nExcluded keywords (case-insensitive): {excluded_list}")
    print("\n" + "="*80)
    
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
    
    # Find groups that match exclusion filters
    blocked_groups = []
    allowed_groups = []
    
    for dialog in dialogs:
        if dialog.is_group:
            group_name_lower = dialog.name.lower()
            is_blocked = False
            matched_filter = None
            
            for excluded_name in excluded_list:
                if excluded_name in group_name_lower:
                    is_blocked = True
                    matched_filter = excluded_name
                    break
            
            if is_blocked:
                blocked_groups.append((dialog.name, matched_filter))
            else:
                allowed_groups.append(dialog.name)
    
    print(f"\n🚫 BLOCKED GROUPS (will NEVER receive messages): {len(blocked_groups)}")
    print("="*80)
    for group_name, filter_matched in blocked_groups:
        print(f"  ❌ {group_name}")
        print(f"     └─ Matched filter: '{filter_matched}'")
    
    print(f"\n✅ ALLOWED GROUPS (will receive messages): {len(allowed_groups)}")
    print("="*80)
    print(f"  (Showing first 20 of {len(allowed_groups)} allowed groups)")
    for i, group_name in enumerate(allowed_groups[:20], 1):
        print(f"  {i}. {group_name}")
    
    if len(allowed_groups) > 20:
        print(f"  ... and {len(allowed_groups) - 20} more")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total groups: {len(blocked_groups) + len(allowed_groups)}")
    print(f"Blocked: {len(blocked_groups)}")
    print(f"Allowed: {len(allowed_groups)}")
    print("="*80 + "\n")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(verify_exclusions())

