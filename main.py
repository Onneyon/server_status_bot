import discord
from discord.ext import tasks, commands
import urllib.request
import json
from yaml import safe_load, dump

from discord.flags import Intents

intents = discord.Intents.default()
intents.message_content = True


class myBot(discord.ext.commands.Bot):
    async def setup_hook(self) -> None:
        self.ready = False
        self.servers = {}

        self.load_config()
        update_status.start()

    def load_config(self):
        with open("servers.yaml", "r") as f:
            self.servers = safe_load(f)
            print(self.servers)

    def save_config(self):
        with open("servers.yaml", "w") as f:
            dump(self.servers, f)

    def add_status(self, api_url, channel_str):
        self.servers[channel_str] = api_url
        self.save_config()


bot = myBot("s!", intents=intents)
with open("token.txt", "r") as f:
    token = f.readline()


@bot.command()
async def add(ctx, api_url):
    channel_str = str(ctx.message.channel.id)
    bot.add_status(api_url, channel_str)


@add.error
async def info_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Error: bad argument')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    bot.ready = True


@tasks.loop(seconds=5.0)
async def update_status():
    if not bot.ready:
        return

    for channel_str in bot.servers:
        api_url = bot.servers[channel_str]

        try:
            page = urllib.request.urlopen(api_url)
            json_return = json.loads(page.read().decode("utf-8"))
            player_count = json_return["data"]["attributes"]["players"]
        except Exception:
            continue

        channel = bot.get_channel(int(channel_str))
        if channel:
            # await channel.edit(topic=f"Players online: {player_count}")
            print(f"{player_count} players in {channel_str} at {api_url}")

try:
    bot.run(token)
except KeyboardInterrupt:
    pass
