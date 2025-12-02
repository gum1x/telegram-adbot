import os
import toml
import asyncio
from telethon import TelegramClient
from telethon import functions, errors

async def join_groups():
    # Load config
    with open("assets/config.toml") as f:
        config = toml.loads(f.read())
    
    phone_number = config["telegram"]["phone_number"]
    api_id = config["telegram"]["api_id"]
    api_hash = config["telegram"]["api_hash"]
    
    # List of groups to join
    groups_to_join = [
        # First batch
        "https://t.me/joinchat/RbV4XhlYiTYhWhitv8oVBA",
        "https://t.me/joinchat/VcmdzNosQoND-xVl",
        "https://t.me/grupocaro",
        "https://t.me/Dreamydrops500",
        "https://t.me/joinchat/v43FkVaXFx84ZWU1",
        "https://t.me/guaranteedgainsswaps",
        "https://t.me/MajesticOnlyFans",
        "https://t.me/OFads",
        "https://t.me/joinchat/gAq-AKQbuR5iZWI0",
        "https://t.me/joinchat/RbV4XhjdURGXRqbemoPYww",
        "https://t.me/findmoregroups",
        "https://t.me/joinchat/RJKVO4o3umKIpDn7",
        # Second batch
        "https://t.me/ofmhackers",
        "https://t.me/OFMJobss",
        "https://t.me/ofmpinboard",
        "https://t.me/PrimeClubOFM",
        "https://t.me/OFMTheHub",
        "https://t.me/ChatterlyOFM",
        "https://t.me/FancyModels",
        "https://t.me/mattsmatrix",
        "https://t.me/SimpHunters",
        "https://t.me/MeloniOFM",
        "https://t.me/whalesofm",
        "https://t.me/OnlyForOfm",
        "https://t.me/ofmrealmxMM",
        "https://t.me/OFMCareers",
        "https://t.me/vaofm",
        "https://t.me/ofmgroup",
        "https://t.me/ofmjobs",
        "https://t.me/OFMgrind",
        "https://t.me/+gF0OM2ZBGTA1NWFh"
    ]
    
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
    print("="*80)
    print(f"Attempting to join {len(groups_to_join)} groups...")
    print("="*80 + "\n")
    
    results = {
        "success": [],
        "already_joined": [],
        "failed": []
    }
    
    for i, invite_link in enumerate(groups_to_join, 1):
        try:
            # Extract invite hash or username
            if "joinchat/" in invite_link:
                # Private invite link with hash (old format)
                hash_code = invite_link.split("joinchat/")[1].split("?")[0]
                print(f"[{i}/{len(groups_to_join)}] Joining: {invite_link}")
                
                try:
                    result = await client(functions.messages.ImportChatInviteRequest(hash=hash_code))
                    print(f"  ✓ Successfully joined!")
                    results["success"].append(invite_link)
                except errors.UsersTooMuchError:
                    print(f"  ⊘ Group is full")
                    results["failed"].append((invite_link, "Group is full"))
                except errors.UserAlreadyParticipantError:
                    print(f"  ✓ Already a member!")
                    results["already_joined"].append(invite_link)
                except errors.InviteHashExpiredError:
                    print(f"  ✗ Invite link expired")
                    results["failed"].append((invite_link, "Invite link expired"))
                except errors.InviteHashInvalidError:
                    print(f"  ✗ Invalid invite link")
                    results["failed"].append((invite_link, "Invalid invite link"))
                except Exception as e:
                    error_msg = str(e)
                    if "already" in error_msg.lower() or "participant" in error_msg.lower():
                        print(f"  ✓ Already a member!")
                        results["already_joined"].append(invite_link)
                    else:
                        print(f"  ✗ Error: {error_msg}")
                        results["failed"].append((invite_link, error_msg))
            
            elif "/+" in invite_link:
                # Private invite link with + format (new format)
                hash_code = invite_link.split("/+")[1].split("?")[0]
                print(f"[{i}/{len(groups_to_join)}] Joining: {invite_link}")
                
                try:
                    result = await client(functions.messages.ImportChatInviteRequest(hash=hash_code))
                    print(f"  ✓ Successfully joined!")
                    results["success"].append(invite_link)
                except errors.UsersTooMuchError:
                    print(f"  ⊘ Group is full")
                    results["failed"].append((invite_link, "Group is full"))
                except errors.UserAlreadyParticipantError:
                    print(f"  ✓ Already a member!")
                    results["already_joined"].append(invite_link)
                except errors.InviteHashExpiredError:
                    print(f"  ✗ Invite link expired")
                    results["failed"].append((invite_link, "Invite link expired"))
                except errors.InviteHashInvalidError:
                    print(f"  ✗ Invalid invite link")
                    results["failed"].append((invite_link, "Invalid invite link"))
                except Exception as e:
                    error_msg = str(e)
                    if "already" in error_msg.lower() or "participant" in error_msg.lower():
                        print(f"  ✓ Already a member!")
                        results["already_joined"].append(invite_link)
                    else:
                        print(f"  ✗ Error: {error_msg}")
                        results["failed"].append((invite_link, error_msg))
            
            elif "t.me/" in invite_link:
                # Public username
                username = invite_link.split("t.me/")[1].split("?")[0].split("/")[0]
                print(f"[{i}/{len(groups_to_join)}] Joining: @{username}")
                
                try:
                    entity = await client.get_entity(username)
                    await client(functions.channels.JoinChannelRequest(entity))
                    print(f"  ✓ Successfully joined @{username}!")
                    results["success"].append(invite_link)
                except errors.UsersTooMuchError:
                    print(f"  ⊘ Group is full")
                    results["failed"].append((invite_link, "Group is full"))
                except errors.UserAlreadyParticipantError:
                    print(f"  ✓ Already a member!")
                    results["already_joined"].append(invite_link)
                except errors.FloodWaitError as e:
                    print(f"  ⚠ Rate limited for {e.seconds} seconds, waiting...")
                    await asyncio.sleep(int(e.seconds))
                    try:
                        await client(functions.channels.JoinChannelRequest(entity))
                        print(f"  ✓ Successfully joined @{username} after wait!")
                        results["success"].append(invite_link)
                    except Exception as retry_error:
                        print(f"  ✗ Error after retry: {str(retry_error)}")
                        results["failed"].append((invite_link, str(retry_error)))
                except Exception as e:
                    error_msg = str(e)
                    if "already" in error_msg.lower() or "participant" in error_msg.lower():
                        print(f"  ✓ Already a member!")
                        results["already_joined"].append(invite_link)
                    else:
                        print(f"  ✗ Error: {error_msg}")
                        results["failed"].append((invite_link, error_msg))
            
            # Small delay between joins
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"  ✗ Unexpected error: {str(e)}")
            results["failed"].append((invite_link, str(e)))
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✓ Successfully joined: {len(results['success'])}")
    print(f"✓ Already joined: {len(results['already_joined'])}")
    print(f"✗ Failed: {len(results['failed'])}")
    
    if results["success"]:
        print(f"\n✅ Newly joined groups:")
        for link in results["success"]:
            print(f"  - {link}")
    
    if results["already_joined"]:
        print(f"\n✅ Already in groups:")
        for link in results["already_joined"]:
            print(f"  - {link}")
    
    if results["failed"]:
        print(f"\n❌ Failed to join:")
        for link, reason in results["failed"]:
            print(f"  - {link}")
            print(f"    Reason: {reason}")
    
    print("="*80 + "\n")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(join_groups())

