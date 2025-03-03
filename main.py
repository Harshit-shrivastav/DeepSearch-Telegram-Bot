import os
import re
import asyncio
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events, functions

# Load environment variables
load_dotenv()

# API credentials for Userbot (For Searching)
API_ID = int(os.getenv("API_ID", "123456"))  # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "your_api_hash")  # Replace with your API_HASH
SESSION_NAME = "userbot_session"

# API credentials for Bot (For User Interaction)
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
BOT_SESSION = "searchBot"

# Limits from env variables
SEARCH_LIMIT = int(os.getenv("SEARCH_LIMIT", "50"))  # Default 50
LINKS_REQUIRED = int(os.getenv("LINKS_REQUIRED", "20"))  # Default 20
TIMEOUT = int(os.getenv("TIMEOUT", "10"))  # Default 10 minutes
MAX_RETRIES = 3  # Max times user can input new group name

# Set up logging
logging.basicConfig(filename="logs.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Initialize Clients
bot = TelegramClient(BOT_SESSION, API_ID, API_HASH).start(bot_token=BOT_TOKEN)
userClient = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Store user search history
user_queries = {}

# Helper function to update progress messages
async def update_progress(event, message, edit_msg):
    try:
        await bot.edit_message(event.chat_id, edit_msg.id, message)
    except Exception as e:
        logging.error(f"Failed to update message: {e}")

# Function to search for channels/groups
async def search_groups(query):
    try:
        result = await userClient(functions.contacts.SearchRequest(q=query, limit=SEARCH_LIMIT))
        usernames = re.findall(r"username='([^']*)'", str(result))
        return usernames
    except Exception as e:
        logging.error(f"Error in search_groups: {e}")
        return []

# Function to search for files in a list of groups
async def search_in_groups_parallel(keyword, usernames, event, edit_msg):
    found_links = []
    sem = asyncio.Semaphore(5)  # Limit to 5 parallel searches

    async def search_single_group(username):
        async with sem:
            links = []
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
                        links.append(f"https://t.me/{username}/{msg.id}")
                if len(links) >= LINKS_REQUIRED:
                    break
            return links

    tasks = [search_single_group(username) for username in usernames]
    results = await asyncio.gather(*tasks)

    for links in results:
        found_links.extend(links)
        if len(found_links) >= LINKS_REQUIRED:
            break

    return found_links

# Command to get logs
@bot.on(events.NewMessage(pattern="/logs"))
async def send_logs(event):
    await event.respond(file="logs.txt")

# Main bot interaction
@bot.on(events.NewMessage)
async def handle_message(event):
    user_id = event.chat_id
    query = event.raw_text.strip()

    if query.startswith("/"):
        return

    user_queries[user_id] = query  # Store initial query
    edit_msg = await event.respond("🔍 Searching for groups...")

    usernames = await search_groups(query)
    
    if not usernames:
        for attempt in range(MAX_RETRIES):
            await update_progress(event, f"⚠️ No groups found for '{query}'. Please enter another group name:", edit_msg)
            response = await bot.wait_for(events.NewMessage(from_users=user_id))
            new_group_name = response.raw_text.strip()

            usernames = await search_groups(new_group_name)
            if usernames:
                break
        else:
            await update_progress(event, "❌ Can't search your query. No groups found.", edit_msg)
            return

    # Start searching for files in found groups
    links = []
    for i, username in enumerate(usernames):
        await update_progress(event, f"📂 Checking for '{query}' in {i+1}/{len(usernames)} groups...", edit_msg)
        new_links = await search_in_groups_parallel(query, [username], event, edit_msg)
        links.extend(new_links)

        if len(links) >= LINKS_REQUIRED:
            break

    # Final results
    if links:
        final_message = f"✅ Found {len(links)} results:\n\n" + "\n".join(links)
    else:
        final_message = "❌ No results found."

    await update_progress(event, final_message, edit_msg)

# Run both clients
async def main():
    async with userClient:
        await bot.run_until_disconnected()

# Start the bot
if __name__ == "__main__":
    userClient.loop.run_until_complete(main())
