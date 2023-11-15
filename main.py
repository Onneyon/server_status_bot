import discord
from discord.ext import tasks, commands
import urllib.request
import json

from discord.flags import Intents

intents = discord.Intents.default()
intents.message_content = True


class myBot(discord.ext.commands.Bot):
    def __init__(self, command_prefix, api_url, channel_id, *, intents, **options):
        super().__init__(command_prefix, intents=intents, **options)
        self.api_url = api_url
        self.channel_id = channel_id
        self.ready = False

    async def setup_hook(self) -> None:
        update_status.start()


bot = myBot("s!", intents=intents, api_url="https://api.battlemetrics.com/servers/16023402",
            channel_id=1003246498751983676)
with open("token.txt", "r") as f:
    token = f.readline()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    bot.ready = True


@tasks.loop(minutes=5.0)
async def update_status():
    if not bot.ready:
        return

    page = urllib.request.urlopen(bot.api_url)
    json_return = json.loads(page.read().decode("utf-8"))
    player_count = json_return["data"]["attributes"]["players"]

    channel = bot.get_channel(bot.channel_id)
    if channel:
        await channel.edit(topic=f"Players online: {player_count}")

try:
    bot.run(token)
except KeyboardInterrupt:
    pass
