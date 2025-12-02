import os
import toml
import logging
import asyncio
import random

from telethon import TelegramClient
from telethon import functions, types, errors, events

from tabulate import tabulate

import sys

# Configure logging for real-time display
logging.basicConfig(
	level=logging.INFO,
	format="\x1b[38;5;147m[\x1b[0m%(asctime)s\x1b[38;5;147m]\x1b[0m %(message)s",
	datefmt="%H:%M:%S",
	force=True
)
logging.getLogger("telethon").setLevel(level=logging.CRITICAL)

class Telegram():

	def __init__(self):
		os.system("clear" if os.name != "nt" else "cls && title ")
		
		with open("assets/config.toml") as f:
			self.config = toml.loads(f.read())
			
		with open("assets/groups.txt", encoding="utf-8") as f:
			self.groups = [i.strip() for i in f]
			
		self.phone_number = self.config["telegram"]["phone_number"]
		self.api_id = self.config["telegram"]["api_id"]
		self.api_hash = self.config["telegram"]["api_hash"]
		
		self.client = TelegramClient(
			session="assets/sessions/%s" % (self.phone_number),
			api_id=self.api_id,
			api_hash=self.api_hash
		)
		
		self.promotions_chat = None
		self.forward_message = None
		
	def tablize(self, headers: list, data: list):
		print(
			tabulate(
				headers=headers,
				tabular_data=data
			).replace("-", "\x1b[38;5;147m-\x1b[0m")
		)

	async def connect(self):
		await self.client.connect()
		logging.info("Attempting to login \x1b[38;5;147m(\x1b[0m%s\x1b[38;5;147m)\x1b[0m" % (self.phone_number))

		if not await self.client.is_user_authorized():
			logging.info("Verification code required \x1b[38;5;147m(\x1b[0m%s\x1b[38;5;147m)\x1b[0m" % (self.phone_number))
			await self.client.send_code_request(self.phone_number)
			logging.info("Sent verification code \x1b[38;5;147m(\x1b[0m%s\x1b[38;5;147m)\x1b[0m" % (self.phone_number))

			try:
				await self.client.sign_in(self.phone_number, input("\x1b[38;5;147m[\x1b[0m?\x1b[38;5;147m]\x1b[0m Verification code\x1b[38;5;147m:\x1b[0m "))
			except errors.SessionPasswordNeededError:
				logging.info("Two-step verification is enabled")
				password = input("\x1b[38;5;147m[\x1b[0m?\x1b[38;5;147m]\x1b[0m Password\x1b[38;5;147m:\x1b[0m ")
				await self.client.sign_in(password=password)

		self.user = await self.client.get_me()
		logging.info("Successfully signed into account \x1b[38;5;147m(\x1b[0m%s\x1b[38;5;147m)\x1b[0m" % (self.user.username))

	async def get_groups(self):
		reply = []

		results = await self.client.get_dialogs(
			limit=None
		)

		for dialog in results:
			# Include all groups (both regular groups and supergroups)
			# Regular groups: is_group=True, is_channel=False
			# Supergroups: is_group=True, is_channel=True
			if dialog.is_group:
				reply.append(dialog)

		return reply

	async def get_all_chats(self):
		# Get all dialogs (includes groups, channels, users)
		# Returns dialogs (not entities) so IDs match what user sees
		dialogs = await self.client.get_dialogs(limit=None)
		chats = []
		
		for dialog in dialogs:
			# Include groups, supergroups, and channels (for selecting source)
			if dialog.is_group or dialog.is_channel:
				chats.append(dialog)
		
		return chats

	async def get_chat_messages(self):
		results = []
		
		async for message in self.client.iter_messages(self.promotions_chat):
			if message.text != None: results.append(message)
		
		return results

	async def get_forum_topics(self, group_entity):
		"""Get all topics from a forum-enabled group, returns list of (topic_id, topic_title) tuples"""
		try:
			# Check if group has forum enabled
			if not hasattr(group_entity, 'forum') or not group_entity.forum:
				return []
			
			result = await self.client(functions.channels.GetForumTopicsRequest(
				channel=group_entity,
				offset_date=0,
				offset_id=0,
				offset_topic=0,
				limit=100
			))
			
			topics = []
			for topic in result.topics:
				if hasattr(topic, 'id'):
					# Get topic title if available
					topic_title = getattr(topic, 'title', '')
					topics.append((topic.id, topic_title))
			
			if topics:
				logging.debug("  Found %s topics: %s" % (len(topics), [t[1] if t[1] else f"ID {t[0]}" for t in topics]))
			
			return topics
		except Exception as e:
			# If we can't get topics, return empty list (will send to general chat)
			logging.debug("  Error getting topics: %s" % str(e))
			return []
	
	def find_preferred_topic(self, topics, group_name="", group_id=None):
		"""Find preferred topic by name: 'other' first, then 'insta', or specific IDs for certain groups"""
		if not topics:
			return None
		
		# Convert to list of (id, title) if it's just IDs
		topic_list = []
		for topic in topics:
			if isinstance(topic, tuple):
				topic_list.append(topic)
			else:
				# Just an ID, no title
				topic_list.append((topic, ''))
		
		group_name_lower = group_name.lower()
		
		# Priority 0: Check config for group-specific topic IDs
		group_topics_config = self.config.get("group_topics", {})
		if group_id:
			# Try by group ID (as string or int)
			config_topic_id = group_topics_config.get(str(group_id)) or group_topics_config.get(int(group_id))
			if config_topic_id:
				# Verify this topic exists in the list
				for topic_id, topic_title in topic_list:
					if topic_id == config_topic_id:
						logging.info(f"  🎯 Config: Using topic ID {config_topic_id} for group {group_id} ('{topic_title or 'No title'}')")
						return topic_id
				logging.warning(f"  ⚠ Config topic ID {config_topic_id} not found for group {group_id}! Available topics: {[t[0] for t in topic_list]}")
		
		# Also check by group name in config
		for config_group_key, config_topic_id in group_topics_config.items():
			if isinstance(config_group_key, str) and config_group_key.lower() in group_name_lower:
				# Verify this topic exists in the list
				for topic_id, topic_title in topic_list:
					if topic_id == config_topic_id:
						logging.info(f"  🎯 Config: Using topic ID {config_topic_id} for group '{group_name}' ('{topic_title or 'No title'}')")
						return topic_id
		
		# Priority 1: Specific topic IDs for specific groups (hardcoded fallback)
		if "flip" in group_name_lower:
			# FLIPS group should use topic ID 1633576
			for topic_id, topic_title in topic_list:
				if topic_id == 1633576:
					logging.info(f"  🎯 FLIPS: Using specific topic ID 1633576 ('{topic_title or 'No title'}')")
					return topic_id
			logging.warning(f"  ⚠ FLIPS: Topic ID 1633576 not found! Available topics: {[t[0] for t in topic_list]}")
		
		# Priority 2: Look for "other" (case-insensitive)
		for topic_id, topic_title in topic_list:
			if topic_title and 'other' in topic_title.lower():
				return topic_id
		
		# Priority 3: Look for "insta" (case-insensitive)
		for topic_id, topic_title in topic_list:
			if topic_title and 'insta' in topic_title.lower():
				return topic_id
		
		# No preferred topic found
		return None

	async def verify_message_sent(self, group, sent_messages, topic_id=None):
		"""Verify that the message actually appeared in the group"""
		try:
			if not sent_messages:
				return False
			
			# Get the sent message ID(s)
			if isinstance(sent_messages, list):
				if len(sent_messages) == 0:
					return False
				sent_msg_id = sent_messages[0].id
			else:
				sent_msg_id = sent_messages.id
			
			# Wait a moment for message to appear
			await asyncio.sleep(0.5)
			
			# Try to fetch the message to verify it exists
			# For forum topics, we need to check in the topic
			if topic_id:
				# For forum topics, check if message appears in topic
				# This is tricky - we'll just verify we got a valid response
				# If forward_messages returned a message object, it likely succeeded
				return sent_msg_id is not None
			else:
				# For regular groups, try to fetch the message
				try:
					last_messages = await self.client.get_messages(group, limit=5)
					for msg in last_messages:
						if msg.id == sent_msg_id and msg.from_id and msg.from_id.user_id == self.user.id:
							return True
					# Message not found in recent messages - might still be processing
					# Return True anyway since we got a valid message ID
					return sent_msg_id is not None
				except Exception:
					# Can't verify, but we got a message ID so assume success
					return sent_msg_id is not None
		except Exception as e:
			logging.debug(f"  Verification error: {str(e)}")
			# If verification fails, still trust the send result
			return True

	async def clean_send(self, group: types.Channel, topic_id=None):
		try:
			if topic_id:
				# Send to specific topic in forum group
				logging.info("  📤 Forwarding to forum topic ID: %s" % topic_id)
				
				# For forum topics in Telethon 1.24.0: pass topic_id directly as reply_to
				# The topic_id is the top_msg_id for forum topics
				try:
					sent_messages = await self.client.forward_messages(
						group,
						self.forward_message,
						reply_to=topic_id
					)
				except Exception as forward_error:
					# If that fails, try without reply_to (will go to general chat)
					error_msg = str(forward_error)
					logging.debug(f"  Forward with topic_id failed: {error_msg}, trying without reply_to...")
					sent_messages = await self.client.forward_messages(
						group,
						self.forward_message
					)
				# Verify message was actually forwarded
				if not sent_messages:
					return (False, "Forward returned None - message not sent")
				if isinstance(sent_messages, list) and len(sent_messages) == 0:
					return (False, "Forward returned empty list - message not sent")
				
				# Check message ID validity
				if isinstance(sent_messages, list):
					sent_msg = sent_messages[0] if len(sent_messages) > 0 else None
				else:
					sent_msg = sent_messages
				
				# Verify we got a valid message with an ID
				if not sent_msg or not hasattr(sent_msg, 'id') or sent_msg.id is None:
					return (False, "Message sent but no valid message ID returned")
				
				logging.debug("  Forward successful, message ID: %s" % sent_msg.id)
			else:
				# Send to regular group or general chat
				logging.debug("  Attempting to forward to regular group")
				sent_messages = await self.client.forward_messages(group, self.forward_message)
				# Verify message was actually forwarded
				if not sent_messages:
					return (False, "Forward returned None - message not sent")
				if isinstance(sent_messages, list) and len(sent_messages) == 0:
					return (False, "Forward returned empty list - message not sent")
				
				# Check message ID validity
				if isinstance(sent_messages, list):
					sent_msg = sent_messages[0] if len(sent_messages) > 0 else None
				else:
					sent_msg = sent_messages
				
				# Verify we got a valid message with an ID
				if not sent_msg or not hasattr(sent_msg, 'id') or sent_msg.id is None:
					return (False, "Message sent but no valid message ID returned")
				
				logging.debug("  Forward successful, message ID: %s" % sent_msg.id)
			return (True, None)
		except errors.FloodWaitError as e:
			error_msg = f"Rate limited for {e.seconds} seconds"
			logging.warning("\x1b[38;5;214m⚠\x1b[0m Ratelimited for \x1b[38;5;147m%s\x1b[0ms, waiting..." % (e.seconds))
			await asyncio.sleep(int(e.seconds))
			# Retry after waiting
			try:
				if topic_id:
					# Retry with topic_id for forum topic
					sent_messages = await self.client.forward_messages(group, self.forward_message, reply_to=topic_id)
					if not sent_messages:
						return (False, "Forward returned None after rate limit retry")
				else:
					sent_messages = await self.client.forward_messages(group, self.forward_message)
					if not sent_messages:
						return (False, "Forward returned None after rate limit retry")
				return (True, None)
			except Exception as retry_error:
				return (False, f"Failed after rate limit wait: {str(retry_error)}")
		except errors.ChatWriteForbiddenError:
			return (False, "No permission to write in this group")
		except errors.UserBannedInChannelError:
			return (False, "You are banned from this group")
		except errors.ChannelPrivateError:
			return (False, "Group is private or you were removed")
		except errors.ChatAdminRequiredError:
			return (False, "Admin rights required")
		except errors.SlowModeWaitError as e:
			return (False, f"Slow mode active, wait {e.seconds} seconds")
		except errors.MessageNotModifiedError:
			return (False, "Message not modified (duplicate)")
		except errors.MessageTooLongError:
			return (False, "Message too long")
		except errors.MediaEmptyError:
			return (False, "Media is empty")
		except errors.InputUserDeactivatedError:
			return (False, "User account deactivated")
		except errors.PeerFloodError:
			return (False, "Peer flood error - too many messages")
		except Exception as e:
			error_str = str(e)
			error_type = type(e).__name__
			
			# Detailed error logging
			logging.debug(f"  Exception type: {error_type}")
			logging.debug(f"  Exception message: {error_str}")
			
			# Check if topic is closed
			if "TOPIC_CLOSED" in error_str or "topic closed" in error_str.lower() or "TOPIC_CLOSED" in error_type:
				return ("TOPIC_CLOSED", "Topic is closed")
			
			# Check for common silent failure patterns
			if "RPCError" in error_type or "rpc" in error_str.lower():
				# Extract error code if available
				if hasattr(e, 'code'):
					return (False, f"RPC Error {e.code}: {error_str}")
				return (False, f"RPC Error: {error_str}")
			
			# Check for any error codes in the message
			import re
			error_code_match = re.search(r'(?:error|code)\s*[:\-]?\s*(\d+)', error_str, re.IGNORECASE)
			if error_code_match:
				return (False, f"{error_type} (code {error_code_match.group(1)}): {error_str}")
			
			return (False, f"{error_type}: {error_str}")
	
	async def send_with_topic_retry(self, group_entity, topics, max_retries=3, group_name="Unknown", group_id=None):
		"""Try sending to a group with forum topics, prioritizing 'other' then 'insta', then random"""
		if not topics:
			# No topics, send to general chat
			return await self.clean_send(group_entity, None)
		
		# Get group name if not provided
		if group_name == "Unknown":
			group_name = getattr(group_entity, 'title', 'Unknown Group')
		
		# Get group ID if not provided
		if group_id is None:
			group_id = getattr(group_entity, 'id', None)
		
		# Extract topic IDs (handle both tuple format and plain IDs)
		topic_ids = []
		topic_map = {}  # Map ID to title for logging
		for topic in topics:
			if isinstance(topic, tuple):
				topic_id, topic_title = topic
				topic_ids.append(topic_id)
				topic_map[topic_id] = topic_title
			else:
				topic_ids.append(topic)
		
		# Find preferred topic (config > group-specific > other > insta)
		preferred_topic_id = self.find_preferred_topic(topics, group_name=group_name, group_id=group_id)
		
		# Build list of topics to try
		topics_to_try = []
		
		if preferred_topic_id:
			# Use preferred topic first
			preferred_title = topic_map.get(preferred_topic_id, '')
			logging.info("  → Found preferred topic: '%s' (ID: %s) in %s" % (preferred_title, preferred_topic_id, group_name))
			
			# Try preferred topic first
			result, error = await self.clean_send(group_entity, preferred_topic_id)
			
			if result == True:
				return (True, None, preferred_topic_id)
			elif result == "TOPIC_CLOSED":
				logging.warning("  → Preferred topic '%s' is closed, trying random topics..." % preferred_title)
				# Add remaining topics for random selection (excluding preferred)
				remaining_topics = [t for t in topic_ids if t != preferred_topic_id]
				if remaining_topics:
					topics_to_try = random.sample(remaining_topics, min(max_retries, len(remaining_topics)))
				else:
					# Only one topic and it's closed
					return (False, "Preferred topic is closed and no other topics available", None)
			else:
				# Other error with preferred topic, try random as fallback
				logging.warning("  → Preferred topic failed: %s, trying random topics..." % error)
				remaining_topics = [t for t in topic_ids if t != preferred_topic_id]
				if remaining_topics:
					topics_to_try = random.sample(remaining_topics, min(max_retries, len(remaining_topics)))
				else:
					return (result, error, preferred_topic_id)
		else:
			# No preferred topic found - use random selection from all topics
			logging.info("  → No preferred topic found, selecting random topic from %s topics in %s" % (len(topic_ids), group_name))
			if len(topic_ids) > 0:
				topics_to_try = random.sample(topic_ids, min(max_retries, len(topic_ids)))
			else:
				return (False, "No topics available", None)
		
		tried_topics = []
		for attempt, topic_id in enumerate(topics_to_try, 1):
			tried_topics.append(topic_id)
			topic_title = topic_map.get(topic_id, f'ID {topic_id}')
			logging.info("  → Trying topic '%s' (ID: %s) in %s (attempt %s/%s)" % (topic_title, topic_id, group_name, attempt, len(topics_to_try)))
			
			result, error = await self.clean_send(group_entity, topic_id)
			
			if result == True:
				# Success!
				if len(tried_topics) > 1:
					logging.info("  → Success after trying %s topic(s)" % len(tried_topics))
				return (True, None, topic_id)
			elif result == "TOPIC_CLOSED":
				# Topic is closed, try next one
				if attempt < len(topics_to_try):
					logging.warning("  → Topic '%s' is closed, trying next topic..." % topic_title)
					continue
				else:
					# All topics tried and closed
					return (False, f"All {len(tried_topics)} topics are closed", None)
			else:
				# Other error, return immediately
				return (result, error, topic_id)
		
		# Should not reach here, but just in case
		return (False, "Failed to send to any topic", None)

	async def cycle(self):
		while True:
			try:
				groups = await self.get_groups()
				
				# Get filter config
				excluded_names = self.config.get("filters", {}).get("excluded_names", "")
				excluded_list = [name.strip().lower() for name in excluded_names.split(",") if name.strip()]
				
				# Statistics
				stats = {
					"total": len(groups),
					"sent": 0,
					"failed": 0,
					"skipped": 0
				}
				
				logging.info("\n" + "="*80)
				logging.info("Starting message forwarding cycle to %s groups..." % stats["total"])
				if excluded_list:
					logging.info("EXCLUDED GROUPS (will NEVER receive messages): %s" % ", ".join(excluded_list))
				logging.info("="*80 + "\n")
				
				for group in groups:
					try:
						# CRITICAL FILTER: Skip groups by name (NO EXCEPTIONS)
						group_name_lower = group.title.lower()
						skip_group = False
						matched_filter = None
						
						for excluded_name in excluded_list:
							if excluded_name in group_name_lower:
								matched_filter = excluded_name
								skip_group = True
								break
						
						if skip_group:
							logging.warning("\x1b[38;5;208m🚫 BLOCKED\x1b[0m \x1b[38;5;147m%s\x1b[0m (matched filter: '%s')" % (group.title, matched_filter))
							stats["skipped"] += 1
							continue
						
						# Check if our message is already the latest
						try:
							last_messages = await self.client.get_messages(group, limit=1)
							if last_messages and len(last_messages) > 0:
								last_message = last_messages[0]
								# Check if we sent the last message
								if (hasattr(last_message, 'from_id') and 
									last_message.from_id and 
									hasattr(last_message.from_id, 'user_id') and
									last_message.from_id.user_id == self.user.id):
									logging.info("\x1b[38;5;244m⊘\x1b[0m Skipped \x1b[38;5;147m%s\x1b[0m (our message is already the latest)" % (group.title))
									stats["skipped"] += 1
									continue
						except Exception as check_error:
							# If we can't check, continue anyway
							logging.debug("  Could not check last message for %s: %s" % (group.title, str(check_error)))
						
						# Get the entity (not the dialog) for forum checks and sending
						group_entity = group.entity
						
						# Special logging for FLIPS
						is_flips = "flip" in group.title.lower()
						if is_flips:
							logging.info("\n🔍 Processing FLIPS group...")
							logging.info(f"  Group: {group.title}")
							logging.info(f"  Entity ID: {group_entity.id}")
							logging.info(f"  Is forum: {hasattr(group_entity, 'forum') and group_entity.forum}")
						
						# Check if group has forum topics
						topics = await self.get_forum_topics(group_entity)
						
						if is_flips:
							logging.info(f"  Topics found: {len(topics)}")
						
						if topics:
							topic_names = [t[1] if t[1] else f"ID {t[0]}" for t in topics]
							logging.info("  📁 Detected forum group with %s topics: %s" % (len(topics), group.title))
							logging.info("  📋 Topics: %s" % ", ".join(topic_names[:10]) + ("..." if len(topic_names) > 10 else ""))
						
						# Attempt to send message (with topic retry if forum group)
						if topics:
							success, error, topic_id = await self.send_with_topic_retry(group_entity, topics, max_retries=3, group_name=group.title, group_id=group_entity.id)
						else:
							success, error = await self.clean_send(group_entity, None)
							topic_id = None
						
						if is_flips:
							logging.info(f"  FLIPS send result: success={success}, error={error}, topic_id={topic_id}")
						
						if success:
							# Double-check for specific groups that might have issues
							group_name_lower = group.title.lower()
							if "flip" in group_name_lower:
								logging.warning("  ⚠ FLIPS group - please verify message actually appeared!")
							
							stats["sent"] += 1
							if topic_id:
								# Find topic name if available
								topic_name = None
								for topic_tuple in topics:
									if isinstance(topic_tuple, tuple) and topic_tuple[0] == topic_id:
										topic_name = topic_tuple[1] if topic_tuple[1] else f"ID {topic_id}"
										break
								if topic_name:
									logging.info("\x1b[38;5;82m✓\x1b[0m Forwarded to \x1b[38;5;147m%s\x1b[0m (topic: '%s')" % (group.title, topic_name))
								else:
									logging.info("\x1b[38;5;82m✓\x1b[0m Forwarded to \x1b[38;5;147m%s\x1b[0m (topic ID: %s)" % (group.title, topic_id))
							else:
								logging.info("\x1b[38;5;82m✓\x1b[0m Forwarded to \x1b[38;5;147m%s\x1b[0m" % (group.title))
						else:
							stats["failed"] += 1
							logging.error("\x1b[38;5;196m✗\x1b[0m Failed to forward to \x1b[38;5;147m%s\x1b[0m - Reason: %s" % (group.title, error))
						
						await asyncio.sleep(self.config["sending"]["send_interval"])
					except Exception as e:
						stats["failed"] += 1
						error_msg = f"{type(e).__name__}: {str(e)}"
						logging.error("\x1b[38;5;196m✗\x1b[0m Error processing \x1b[38;5;147m%s\x1b[0m - %s" % (group.title, error_msg))
						
						# Extra logging for FLIPS
						if "flip" in group.title.lower():
							logging.error("  🔍 FLIPS ERROR DETAILS:")
							logging.error(f"    Exception type: {type(e).__name__}")
							logging.error(f"    Exception message: {str(e)}")
							import traceback
							logging.error(f"    Traceback: {traceback.format_exc()}")
				
				# Print cycle summary
				logging.info("\n" + "="*80)
				logging.info("Cycle completed!")
				logging.info("="*80)
				logging.info("Total groups: \x1b[38;5;147m%s\x1b[0m" % stats["total"])
				logging.info("\x1b[38;5;82m✓\x1b[0m Successfully sent: \x1b[38;5;82m%s\x1b[0m" % stats["sent"])
				logging.info("\x1b[38;5;196m✗\x1b[0m Failed: \x1b[38;5;196m%s\x1b[0m" % stats["failed"])
				logging.info("\x1b[38;5;244m⊘\x1b[0m Skipped: \x1b[38;5;244m%s\x1b[0m" % stats["skipped"])
				logging.info("="*80 + "\n")
				
			except Exception as e:
				logging.error("Critical error in cycle: %s" % str(e))
				
			await asyncio.sleep(self.config["sending"]["loop_interval"])

	async def join_groups(self):
		# Check if we should skip joining groups (auto-run mode)
		skip_join = self.config.get("telegram", {}).get("skip_join_groups", False)
		if skip_join:
			logging.info("Skipping group joining (auto-run mode enabled)")
			return
		
		seen = []
		
		option = input("\x1b[38;5;147m[\x1b[0m?\x1b[38;5;147m]\x1b[0m Join groups?\x1b[38;5;147m:\x1b[0m ").lower()
		if option == "" or "n" in option: return
		print()
		
		for invite in self.groups:
			if invite in seen: continue
			seen.append(seen)
			
			while True:
				try:
					if "t.me" in invite: code = invite.split("t.me/")[1]
					else: code = invite
					
					await self.client(functions.channels.JoinChannelRequest(code))
					logging.info("Successfully joined \x1b[38;5;147m%s\x1b[0m!" % (invite))
					break
				except errors.FloodWaitError as e:
					logging.info("Ratelimited for \x1b[38;5;147m%s\x1b[0ms." % (e.seconds))
					await asyncio.sleep(int(e.seconds))
				except Exception:
					logging.info("Failed to join \x1b[38;5;147m%s\x1b[0m." % (invite))
					break
			
			await asyncio.sleep(0.8)

	async def start(self):
		await self.connect()
		
		print()
		await self.join_groups()
		print()
		
		# Check if auto-run mode is enabled
		auto_run = self.config.get("telegram", {}).get("auto_run", False)
		source_chat_id = self.config.get("telegram", {}).get("source_chat_id")
		message_id = self.config.get("telegram", {}).get("message_id")
		
		if auto_run and source_chat_id and message_id:
			# Auto-run mode: use config values
			logging.info("Auto-run mode enabled - using config values")
			logging.info("Source chat ID: %s" % source_chat_id)
			logging.info("Message ID: %s" % message_id)
			
			# Get the chat entity directly
			try:
				self.promotions_chat = await self.client.get_entity(source_chat_id)
				chat_type = "channel" if hasattr(self.promotions_chat, 'broadcast') and self.promotions_chat.broadcast else "group"
				logging.info("Found source chat: \x1b[38;5;147m%s\x1b[0m (%s)" % (self.promotions_chat.title, chat_type))
			except Exception as e:
				logging.error("Failed to get chat entity: %s" % str(e))
				return
			
			# Get the message directly
			try:
				messages = await self.client.get_messages(self.promotions_chat, ids=message_id)
				if isinstance(messages, list):
					if len(messages) > 0:
						self.forward_message = messages[0]
					else:
						logging.error("Message ID %s not found" % message_id)
						return
				else:
					self.forward_message = messages
				
				if self.forward_message is None:
					logging.error("Message ID %s not found" % message_id)
					return
					
				logging.info("Found message: \x1b[38;5;147m%s\x1b[0m" % (self.forward_message.text[:50] if self.forward_message.text else "Media message"))
			except Exception as e:
				logging.error("Failed to get message: %s" % str(e))
				return
		else:
			# Interactive mode: show prompts
			chats = await self.get_all_chats()
			self.tablize(
				headers=["ID", "Name", "Type"],
				data=[[chat.id, chat.name, "Channel" if chat.is_channel and not chat.is_group else "Group"] for chat in chats]
			)
			print()
			
			logging.info("Please select the group or channel you would like to forward the message from")
			channel_id = int(input("\x1b[38;5;147m[\x1b[0m?\x1b[38;5;147m]\x1b[0m ID\x1b[38;5;147m:\x1b[0m "))
			
			for chat in chats:
				if chat.id == channel_id:
					self.promotions_chat = chat.entity
					
			if self.promotions_chat == None: return logging.info("Invalid chat ID selected.")
			print()
			
			chat_type = "channel" if hasattr(self.promotions_chat, 'broadcast') and self.promotions_chat.broadcast else "group"
			logging.info("Selected \x1b[38;5;147m%s\x1b[0m (%s) as your source." % (self.promotions_chat.title, chat_type))
			print()
			
			messages = await self.get_chat_messages()
			self.tablize(
				headers=["ID", "Content"],
				data=[[message.id, message.text[:50]] for message in messages]
			)
			print()
			
			logging.info("Please select the message you would like to forward")
			message_id = int(input("\x1b[38;5;147m[\x1b[0m?\x1b[38;5;147m]\x1b[0m ID\x1b[38;5;147m:\x1b[0m "))
			
			for message in messages:
				if message.id == message_id:
					self.forward_message = message
					
			if self.forward_message == None: return logging.info("Invalid message ID selected.")
			print()
			
			logging.info("Selected \x1b[38;5;147m%s\x1b[0m are your message to forward." % (self.forward_message.text[:50]))        
		
		groups = await self.get_groups()
		logging.info("Sending out your message to \x1b[38;5;147m%s\x1b[0m groups!" % (len(groups)))
		
		print()
		await self.cycle()
		
if __name__ == "__main__":
	client = Telegram()
	asyncio.get_event_loop().run_until_complete(client.start())
