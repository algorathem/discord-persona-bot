import discord
from discord.ext import commands
import threading
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

BOT_OWNER_ID = os.getenv("BOT_OWNER_ID")
if not BOT_OWNER_ID:
    print("ERROR: BOT_OWNER_ID environment variable is not set!")
    sys.exit(1)
BOT_OWNER_ID = int(BOT_OWNER_ID)

ADMIN_ROLE_NAME = "Admin"
NEW_MEMBER_ROLE = "Explorer"
FELLOW_ROLE = "Fellow"
REACTION_EMOJI = "🖥️" 

AVATARS = {
    "scholar": {
        "name": "The Scholar",
        "avatar": "https://i.imgur.com/tO0Tijd.jpeg"
    },
    "herald": {
        "name": "The Herald",
        "avatar": "https://i.imgur.com/G7vZqvx.jpeg"
    },
    "envoy": {
        "name": "The Envoy",
        "avatar": "https://i.imgur.com/YpxP051.jpeg"
    }
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Cache webhooks per channel
webhooks_cache = {}  

def owner_or_admin():

    async def predicate(ctx):
        if ctx.author.id == BOT_OWNER_ID:
            return True
        return ADMIN_ROLE_NAME in [role.name for role in ctx.author.roles]

    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.event
async def on_member_join(member):
    """Assign New Member role automatically"""
    role = discord.utils.get(member.guild.roles, name=NEW_MEMBER_ROLE)
    if role:
        await member.add_roles(role)
        print(f"Assigned {NEW_MEMBER_ROLE} to {member.name}")

@bot.event
async def on_raw_reaction_add(payload):
    """Assign Fellow role when user reacts with the specific emoji"""
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    if str(payload.emoji) == REACTION_EMOJI:
        role = discord.utils.get(guild.roles, name=FELLOW_ROLE)
        if role:
            await member.add_roles(role)
            print(f"Assigned {FELLOW_ROLE} to {member.name}")

async def get_webhook(channel, avatar_name):
    """Get or create a webhook for the channel and cache it."""
    if channel.id in webhooks_cache:
        return webhooks_cache[channel.id]

    webhook = await channel.create_webhook(name=avatar_name)
    webhooks_cache[channel.id] = webhook
    return webhook

@bot.command()
@owner_or_admin()
async def say(ctx, avatar_name: str, *, message: str):
    """Usage: !say scholar Hello world"""
    avatar_name = avatar_name.lower()

    if avatar_name not in AVATARS:
        await ctx.send(
            f"Unknown avatar. Available: {', '.join(AVATARS.keys())}")
        return

    avatar = AVATARS[avatar_name]

    try:
        webhook = await get_webhook(ctx.channel, avatar["name"])
        await webhook.send(content=message,
                           username=avatar["name"],
                           avatar_url=avatar["avatar"])
    except discord.DiscordException as e:
        await ctx.send(f"Failed to send message: {e}")

    try:
        await ctx.message.delete()
    except discord.DiscordException:
        pass

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server).start()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: DISCORD_TOKEN environment variable is not set!")
    sys.exit(1)

bot.run(TOKEN)
