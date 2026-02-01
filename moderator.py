import discord
import os
import json
from discord.ext import commands
from datetime import datetime, timedelta

# CONTENT WARNING: the following moderation script may reference words that are extremely harmful in social contexts for the pure purpose of moderation. if you feel triggered by any of the content, speak to someone about it.

intents = discord.Intents.default()
intents.members = True  # Required for member events
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)
GUILD_ID = 1446301256913256510

LOG_CHANNEL = 1467395713435697358

MEMORY_FILEPATH = "./data/mod.json"
Memory = {}

if os.path.exists(MEMORY_FILEPATH):
    with open(MEMORY_FILEPATH, "r") as f:  # <-- use open(), not os.open()
        Memory = json.load(f)

@bot.event
async def on_ready():
    # Sync the slash commands to your guild
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user} and commands synced!")



@bot.tree.command(
    name="kill",
    description="Kill a user(bans them).\nCan only be used by those with moderator permissions",
    guild=discord.Object(id=GUILD_ID)
)
async def kill(
    interaction: discord.Interaction,
    user: discord.Member, # The person to kill
    why: discord.Optional[str] = None
):
    try:
        await user.ban(reason=why or "")
        await interaction.guild.get_channel(LOG_CHANNEL).send(f"{user.display_name} was banned")
        await interaction.response.send_message("killed", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("Could not kill", ephemeral=True)

@bot.tree.command(
    name="revive",
    description="Uhh... hire a necromancer or smth for this one folks",
    guild=discord.Object(id=GUILD_ID)
)
async def revive(
    interaction: discord.Interaction,
    user: discord.User,
    send_invite: discord.Optional[bool] = True
):
    try:
        await interaction.guild.unban(user=user)
        await interaction.guild.get_channel(LOG_CHANNEL).send(f"{user.display_name} was unbanned")

        if not user.bot:
            try:
                await user.send(f"You are unbanned from {interaction.guild.name}.")
                if send_invite:
                    invite = await interaction.channel.create_invite(
                        max_age=604800,
                        max_uses=1
                    )
                    await user.send(
                        f"Here is your invite (expires in 7 days):\n{invite}"
                    )
            except discord.Forbidden:
                pass  # DMs closed, fate accepted

        await interaction.response.send_message(
            f"Revived {user.mention}.",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "I lack permission to perform resurrection.",
            ephemeral=True
        )

@bot.tree.command(
    name="put_to_sleep",
    description="put specified user to sleep for a specified about of seconds",
    guild=discord.Object(id=GUILD_ID)
)
async def put_to_sleep(
    interaction: discord.Interaction,
    user: discord.Member, # who to timeout
    time: float # how long
):
    try:
        future_time = datetime.now() + timedelta(seconds=123.456)
        await user.timeout(future_time)
        await interaction.response.send_message(f"put {user.display_name} to sleep for {str(time)} seconds")
        await interaction.guild.get_channel(LOG_CHANNEL).send(f"{user} was timed out/put to sleep for {str(time)}")
    except discord.Forbidden:
        await interaction.response.send_message(f"could not put {user.display_name} to sleep")


bot.run("MTQ2NzM2MDU4OTA5MjQ5MTM0Ng.GxW5k_.jdxgEyxtdmECCEPm7USGUHi47Tems_ge34PYt4")
