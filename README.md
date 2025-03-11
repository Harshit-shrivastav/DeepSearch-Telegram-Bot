# 🔍 Deep Search Bot 🤖

Welcome to the **Telegram DeepSearch Bot** repository! This bot helps you search for specific keywords across multiple Telegram groups and channels. It’s designed to find media files (photos, videos, documents) that match your query and provide direct links to them. 🚀

---

## 🌟 Features

- **Search Across Groups**: Search for keywords in multiple Telegram groups/channels simultaneously.
- **Media Matching**: Finds media files (photos, videos, documents) with matching captions or filenames.
- **Link Generation**: Provides direct Telegram links to the matched media.
- **Customizable Limits**: Set limits for the number of groups to search, links to find, and search timeout.
- **Logging**: Detailed logs for debugging and tracking bot activity.
- **User-Friendly**: Interactive messages guide users through the search process.

---

## 🛠️ Setup

### Prerequisites

- Python 3.8 or higher
- A Telegram API ID and Hash (get it from [my.telegram.org](https://my.telegram.org))
- A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Harshit-shrivastav/DeepSearch-Telegram-Bot
   cd telegram-group-search-bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your credentials:
   ```env
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

---

## 🚀 Usage

1. Start the bot by sending `/start` in Telegram.
2. Enter a keyword or phrase to search for.
3. The bot will search across Telegram groups/channels and provide links to matching media files.
4. Use `/logs` to retrieve the bot's log file for debugging.

---

## ⚙️ Configuration

You can customize the bot's behavior by modifying the following variables in the code:

- `SEARCH_LIMIT`: Maximum number of groups to search initially.
- `MAX_LINKS`: Stop searching after finding this many links.
- `SEARCH_TIMEOUT`: Stop searching after this many minutes.
- `MAX_RETRIES`: Maximum retries for asking user input.

---

## 📜 Logs

The bot logs all activities in `logs.txt`. You can retrieve the logs by sending the `/logs` command.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

For questions or feedback, reach out to [I@h-s.site](mailto:I@h-s.site).

---

Happy searching! 🎉
