import logging
import asyncio
import sys
import os
from dotenv import load_dotenv

import discord
from rss_bot.utils import load_config, get_bot_token
from rss_bot.rss import RSSReader
from rss_bot.bot import DiscordBot

# Load .env automatically
load_dotenv()  # reads DISCORD_TOKEN into os.environ

CONFIG_PATH = "config.yaml"  # default to local config.yaml


async def initialize_bot() -> None:
    """Initializes and starts the Discord bot with RSS integration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("discord").setLevel(logging.INFO)

    try:
        # Load bot token from env
        bot_token = os.getenv("DISCORD_TOKEN")
        if not bot_token:
            raise ValueError("DISCORD_TOKEN not set in environment or .env file")

        # Load config.yaml
        config = load_config(CONFIG_PATH)

        # Initialize RSS reader
        rss_reader = RSSReader(config)
        await rss_reader.setup()

        # Initialize Discord bot
        intents = discord.Intents.default()
        bot = DiscordBot(rss_reader, intents=intents, root_logger=True)

        logging.info("Bot is starting...")
        await bot.start(bot_token)

    except Exception as e:
        logging.critical("An unrecoverable error occurred: %s", e, exc_info=True)
        sys.exit(1)


def main():
    try:
        asyncio.run(initialize_bot())
    except KeyboardInterrupt:
        logging.info("Bot shutting down gracefully.")


if __name__ == "__main__":
    main()
