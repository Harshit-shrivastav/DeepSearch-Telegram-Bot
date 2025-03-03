import os
import re
import asyncio
import time
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events, functions

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID", "123456"))  # Change this
API_HASH = os.getenv("API_HASH", "your_api_hash")  # Change this
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")  # Bot token

SEARCH_LIMIT = 50   # Max groups to search initially
MAX_LINKS = 20      # Stop searching after this many links
SEARCH_TIMEOUT = 10  # Stop searching after this many minutes
MAX_RETRIES = 3      # Max retries for asking user input

# Logging setup
logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize clients
botClient = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
userClient = TelegramClient("userbot", API_ID, API_HASH)

@botClient.on(events.NewMessage)
async def handle_message(event):
    """Handles user messages and initiates search."""
    try:
        user_query = event.message.text.strip()
        if user_query.startswith("/"):
            return  # Ignore commands

        logging.info(f"User query received: {user_query}")

        progress_msg = await event.reply("🔍 Searching for groups...")  # Send initial message
        found_links = []
        retry_count = 0

        while retry_count < MAX_RETRIES:
            usernames = await search_groups(user_query)

            if usernames:
                await progress_msg.edit(f"✅ {len(usernames)} usernames found.\nNow searching for '{user_query}' in these groups...")
                
                result_msg = await event.reply("🔍 Searching... No links found yet.")  # Message for links
                found_links = await search_in_groups(user_query, usernames, progress_msg, result_msg)

                if len(found_links) >= MAX_LINKS:
                    break  # Stop if we got enough links
                else:
                    await progress_msg.edit(f"🔍 Found {len(found_links)} links so far, {MAX_LINKS - len(found_links)} more needed.\nNow tell me another group/channel name to search.")
                    response = await botClient.wait_for(events.NewMessage(event.chat_id))
                    user_query = response.message.text.strip()
                    retry_count += 1
                    await progress_msg.edit(f"📌 Searching for '{user_query}' now...")
            else:
                retry_count += 1
                await progress_msg.edit(f"❌ No usernames found. Please enter another group or channel name.")

                if retry_count < MAX_RETRIES:
                    response = await botClient.wait_for(events.NewMessage(event.chat_id))
                    user_query = response.message.text.strip()
                    await progress_msg.edit(f"🔎 Searching for '{user_query}' now...")
                else:
                    await progress_msg.edit("❌ Query not found.")
                    return

        # Final message update
        if found_links:
            await result_msg.edit("✅ Search complete!\nHere are the final links:\n" + "\n".join(found_links))
        else:
            await result_msg.edit("❌ Query not found.")

    except Exception as e:
        logging.error(f"Error in handle_message: {str(e)}")
        await event.reply("An error occurred. Please try again later.")


async def search_groups(query):
    """Search for channels/groups matching the query and return usernames."""
    try:
        async with userClient:
            search_result = await userClient(functions.contacts.SearchRequest(q=query, limit=SEARCH_LIMIT))
            search_json = str(search_result)
            usernames = re.findall(r"username='([^']*)'", search_json)  # Extract usernames
            logging.info(f"Search groups found usernames: {usernames}")
            return usernames
    except Exception as e:
        logging.error(f"Error in search_groups: {str(e)}")
        return []


async def search_in_groups(keyword, usernames, progress_msg, result_msg):
    """Search for keyword in found groups one by one until MAX_LINKS found."""
    try:
        start_time = time.time()
        found_links = []
        remaining_links = MAX_LINKS  # We will decrement this as we find links

        async with userClient:
            for index, username in enumerate(usernames):
                if remaining_links <= 0 or (time.time() - start_time) > (SEARCH_TIMEOUT * 60):
                    break  # Stop if max links or time exceeded

                await progress_msg.edit(f"📂 Checking for '{keyword}' in group {index+1}/{len(usernames)}: {username}...")

                group_links = []

                async for msg in userClient.iter_messages(username, limit=500):
                    if msg.media and (msg.photo or msg.video or msg.document):
                        caption_match = msg.text and keyword.lower() in msg.text.lower()
                        file_match = (
                            hasattr(msg, "document")
                            and msg.document
                            and msg.file
                            and msg.file.name
                            and keyword.lower() in msg.file.name.lower()
                        )

                        if caption_match or file_match:
                            group_links.append(f"https://t.me/{username}/{msg.id}")
                            remaining_links -= 1

                    if remaining_links <= 0:
                        break  # Stop if enough links found

                if group_links:
                    found_links.extend(group_links)
                    await progress_msg.edit(f"✅ Found {len(group_links)} links in {username}. Total links found: {len(found_links)}.\n🔍 Searching more...")

                    # Update result message
                    await result_msg.edit("🔍 Links found so far:\n" + "\n".join(found_links))

        return found_links

    except Exception as e:
        logging.error(f"Error in search_in_groups: {str(e)}")
        return []


@botClient.on(events.NewMessage(pattern="/logs"))
async def send_logs(event):
    """Sends the log file to the user."""
    try:
        await event.reply(file="logs.txt")
    except Exception as e:
        logging.error(f"Error in send_logs: {str(e)}")
        await event.reply("Couldn't retrieve logs.")


# Start both clients
async def main():
    await userClient.start()
    await botClient.run_until_disconnected()

asyncio.run(main())
