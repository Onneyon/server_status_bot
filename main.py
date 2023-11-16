import discord
from discord.ext import tasks, commands
import urllib.request
import json
from yaml import safe_load, dump
from pathlib import Path

intents = discord.Intents.default()
intents.message_content = True


class myBot(discord.ext.commands.Bot):
    async def setup_hook(self) -> None:
        self.ready = False
        self.servers = {}

        self.load_config()
        update_status.start()

    def load_config(self):
        try:
            with open("servers.yaml", "r") as f:
                raw = safe_load(f)
                self.servers = raw if raw else {}
        except FileNotFoundError:
            Path("servers.yaml").touch()

    def save_config(self):
        with open("servers.yaml", "w") as f:
            dump(self.servers, f)

    def add_status(self, api_url, channel_str):
        self.servers[channel_str] = api_url
        self.save_config()

    def remove_status(self, channel_str):
        del self.servers[channel_str]
        self.save_config()


bot = myBot("s!", intents=intents)
with open("token.txt", "r") as f:
    token = f.readline()


@bot.command()
async def add(ctx, api_url):
    channel_str = str(ctx.message.channel.id)
    bot.add_status(api_url, channel_str)
    await ctx.send("Added player counter to this channel, status may take up to 5 mins to be updated")


@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Error: this command takes one argument')


@bot.command()
async def remove(ctx):
    channel_str = str(ctx.message.channel.id)
    bot.remove_status(channel_str)
    await ctx.send("Removed player counter from this channel, you are free to edit its description")


@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Error: this command does not take an argument')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    bot.ready = True


@tasks.loop(minutes=5.0)
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
            await channel.edit(topic=f"Players online: {player_count}")

try:
    bot.run(token)
except KeyboardInterrupt:
    pass
