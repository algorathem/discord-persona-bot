import os
import sys
import logging
import asyncio

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from rss_bot.utils import load_config
from rss_bot.rss import RSSReader
from rss_bot.message import format_entry_for_discord
from rss_bot.models import FeedConfig

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID"))

CONFIG_PATH = "config.yaml"

ADMIN_ROLE_NAME = "Admin"
NEW_MEMBER_ROLE = "Explorer"
FELLOW_ROLE = "Fellow"
REACTION_EMOJI = "🖥️"

AVATARS = {
    "scholar": {"name": "The Scholar", "avatar": "https://i.imgur.com/tO0Tijd.jpeg"},
    "herald": {"name": "The Herald", "avatar": "https://i.imgur.com/G7vZqvx.jpeg"},
    "envoy": {"name": "The Envoy", "avatar": "https://i.imgur.com/YpxP051.jpeg"},
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True

class CombinedBot(commands.Bot):
    def __init__(self, rss_reader: RSSReader):
        super().__init__(command_prefix="!", intents=intents)
        self.rss_reader = rss_reader
        self.webhooks_cache = {}

    async def setup_hook(self):
        self.check_feeds.start()

    async def on_ready(self):
        logging.info("Logged in as %s (%s)", self.user, self.user.id)

    #RSS Feature

    @tasks.loop(minutes=5)
    async def check_feeds(self):
        await self.rss_reader.update_feeds(scheduled=True)
        await asyncio.gather(*[
            self.process_feed(feed)
            for feed in self.rss_reader.config.feeds
        ])

    async def process_feed(self, feed: FeedConfig):
        entries = await self.rss_reader.get_unread_entries(feed.feed_url)
        if not entries:
            return

        channel = self.get_channel(int(feed.channel_id))
        if not isinstance(channel, discord.TextChannel):
            return

        for entry in reversed(entries):
            await channel.send(embed=format_entry_for_discord(entry))

        await self.rss_reader.mark_entries_as_read(entries)

    #Persona Feature

    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name=NEW_MEMBER_ROLE)
        if role:
            await member.add_roles(role)

    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.user.id:
            return
        guild = self.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member and str(payload.emoji) == REACTION_EMOJI:
            role = discord.utils.get(guild.roles, name=FELLOW_ROLE)
            if role:
                await member.add_roles(role)

    async def get_webhook(self, channel, name):
        if channel.id not in self.webhooks_cache:
            self.webhooks_cache[channel.id] = await channel.create_webhook(name=name)
        return self.webhooks_cache[channel.id]

def owner_or_admin():
    async def predicate(ctx):
        return ctx.author.id == BOT_OWNER_ID or any(
            r.name == ADMIN_ROLE_NAME for r in ctx.author.roles
        )
    return commands.check(predicate)

@commands.command()
@owner_or_admin()
async def say(ctx, avatar: str, *, message: str):
    avatar = avatar.lower()
    if avatar not in AVATARS:
        return await ctx.send("Invalid avatar")

    data = AVATARS[avatar]
    bot: CombinedBot = ctx.bot
    webhook = await bot.get_webhook(ctx.channel, data["name"])
    await webhook.send(
        content=message,
        username=data["name"],
        avatar_url=data["avatar"],
    )
    await ctx.message.delete()

async def main():
    logging.basicConfig(level=logging.INFO)

    config = load_config(CONFIG_PATH)
    rss_reader = RSSReader(config)
    await rss_reader.setup()

    bot = CombinedBot(rss_reader)
    bot.add_command(say)

    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
