import discord
import os
import json
import time
from discord.ext import commands
from datetime import datetime, timedelta


WEEK = 604800
UPDATE_LOG = "Moderator v1.0.0 beta by Morxe0 \nAdded permission checking on '/kill', '/revive', and '/put_to_sleep'."

# CONTENT WARNING: the following moderation script may reference words that are extremely harmful in social contexts for the pure purpose of moderation. if you feel triggered by any of the content, speak to someone about it.

intents = discord.Intents.default()
intents.members = True  # Required for member events
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

guild = "./GUILD.json" #make your own guild.json, "id" is the guild id, "LOG" is the server log channel

if os.path.exists(guild):
    with open(guild, "r") as f:
        fil = json.load(f)
        GUILD_ID = fil["id"]
        LOG_CHANNEL = fil["LOG"]

k = "./ACCESS_KEY.txt" #discord access id
KEY = ""
if os.path.exists(k):
    with open(k, "r") as f:
        KEY = f.readlines()[0].strip()

MEMORY_FILEPATH = "./data/mem.json"
TRIGGERWORDS_FILEPATH = "./data/triggerwords.json"
Memory = {}
Triggerwords = {}
if os.path.exists(MEMORY_FILEPATH):
    with open(MEMORY_FILEPATH, "r") as f:  # <-- use open(), not os.open()
        Memory = json.load(f)

def _save():
    with open(MEMORY_FILEPATH, "w") as f:
        json.dump(Memory, f, indent=5)

def create_mem_(user: discord.Member):
    Memory[str(user.id)] = {}
    Memory[str(user.id)]["offenses"] = []
    Memory[str(user.id)]["trust_score"] = 1.0
    _save()

class normalizer:
    replacement_table = [
        {
            "r": "1",
            "v": "i"
        },
        {
            "r": "¡",
            "v": "i"
        },
        {
            "r": "@",
            "v": "a"
        },
        {
            "r": "|(",
            "v": "k"
        },
        {
            "r": "!",
            "v": "i"
        },
        {
            "r": "|",
            "v": "i"
        },
        {
            "r": "&",
            "v": "8"
        },
        {
            "r": "0",
            "v": "o"
        },
        {
            "r": "9",
            "v": "g"
        },
        {
            "r": "3",
            "v": "e"
        },
        {
            "r": "$",
            "v": "s"
        },
        {
            "r": "+",
            "v": "t"
        },
        {
            "r": "\\/",
            "v": "v"
        }
    ] # WILL be expanded later after testing
    @classmethod
    def normalized(self, txt: str):
        t = txt.strip()
        for r in self.replacement_table:
            t = t.replace(r["r"], r["v"])
        return t


def calc_trust_score(offenses: list):
    trust = 1.0

    for offense in offenses:
        age = time.time() - offense["ts"]
        weeks = age // WEEK
        decay = weeks * 0.1

        impact = max(0, offense["trust_score_impact"] - decay)
        trust -= impact

    return max(0.0, min(1.0, trust))



if os.path.exists(TRIGGERWORDS_FILEPATH):
    with open(TRIGGERWORDS_FILEPATH, "r") as f:  # <-- use open(), not os.open()
        Triggerwords = json.load(f)

async def tell_off_offending_user(user: discord.Member, word: str, category: str, msg: str):
    if not user.dm_channel:
        await user.create_dm()
    if category == "absolute_worst":
        await user.dm_channel.send(f"# Your message could not be sent.\nYour message that read as follows:\n >{msg}\nCould not be sent as it contains content telling someone to kill themselves. example: {word}. Words like that have no place on the internet.\n-# if you belive this is a mistake, please contact the owner of the server. Thank you.")
        o: list = Memory[str(user.id)]["offenses"]
        o.append({
            "trust_score_impact": 0.5,
            "ts": time.time(),
            "reason": "Encouraged another user to kill/harm themselves.",
            "issuer": bot.user.id
        })
        Memory[str(user.id)]["offenses"] = o
        Memory[str(user.id)]["trust_score"] = calc_trust_score(o)
        _save()
    if category == "very_very_bad":
        await user.dm_channel.send(f"# Your message could not be sent.\nYour message that read as follows:\n >{msg}\nCould not be sent as it contains potentially offensive/sexual content. example: {word}. Words like that are extremely offensive.\n-# if you belive this is a mistake, please contact the owner of the server. Thank you.")
        o: list = Memory[str(user.id)]["offenses"]
        o.append({
            "trust_score_impact": 0.35,
            "ts": time.time(),
            "reason": "Said extremely offensive/sexual word(s).",
            "issuer": bot.user.id
        })
        Memory[str(user.id)]["offenses"] = o
        Memory[str(user.id)]["trust_score"] = calc_trust_score(o)
        _save()
    if category == "bad":
        await user.dm_channel.send(f"# Your message could not be sent.\nYour message that read as follows:\n >{msg}\nCould not be sent as it contains potentially offensive/sexual content. example: {word}. Words like that may be offensive to some groups.\n-# if you belive this is a mistake, please contact the owner of the server. Thank you.")
        o: list = Memory[str(user.id)]["offenses"]
        o.append({
            "trust_score_impact": 0.1,
            "ts": time.time(),
            "reason": "Said mildly offensive/sexual word(s).",
            "issuer": bot.user.id
        })
        Memory[str(user.id)]["offenses"] = o
        Memory[str(user.id)]["trust_score"] = calc_trust_score(o)
        _save()

async def _checks(user: discord.Member, authorizer: discord.Member, guild: discord.Guild):
    if not authorizer.guild_permissions.administrator:
        return 1
    ts = calc_trust_score(Memory[str(user.id)]["offenses"])
    Memory[str(user.id)]["trust_score"] = ts
    if ts <= 0.01:
        await user.ban()
        if not user.dm_channel:
            await user.create_dm()
        await user.dm_channel.send(f"Due to your actions, the moderators of {guild.name} chose to ban you. If you feel this was a mistake, feel free to contact the owners of the server... Please note that in the event that the moderators of this server unban you, you will be notified.")
    elif ts <= 0.5:
        Memory[str(user.id)]["trusted"] = True
    return 0

@bot.event
async def on_ready():
    # Sync the slash commands to your guild
    guild: discord.Guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user} and commands synced!")
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.CustomActivity(name="moderating")
    )

@bot.tree.command(
    name="runchecksonall",
    description="runs the checks on all users.",
    guild=discord.Object(id=GUILD_ID)
)
async def runchecksonall(
    interaction: discord.Interaction
):
    for user in interaction.guild.members:
        resp = await _checks(user, interaction.user, interaction.guild)
        if resp == 1:
            await interaction.response.send_message("You do not have proper permissions.")
            return

@bot.event
async def on_member_join(member):
    create_mem_(member)


@bot.event
async def on_message(msg: discord.Message):
    if str(msg.author.id) not in Memory:
        create_mem_(msg.author)
    txt = normalizer.normalized(msg.content)
    channel = msg.channel
    if not msg.author.bot:
        for word in Triggerwords["absolute_worst"]:
            if word.lower() in txt.lower():
                author = msg.author
                await msg.delete()
                await tell_off_offending_user(author, word, "absolute_worst", txt)
                await channel.send(f"a message from {author.mention} was deleted by {bot.user.mention}.")
                break
        for word in Triggerwords["very_very_bad"]:
            if word.lower() in txt.lower():
                author = msg.author
                await msg.delete()
                await tell_off_offending_user(author, word, "very_very_bad", txt)
                await channel.send(f"a message from {author.mention} was deleted by {bot.user.mention}.")
                break
        for word in Triggerwords["bad"]:
            if word.lower() in txt.lower():
                author = msg.author
                await msg.delete()
                await tell_off_offending_user(author, word, "bad", txt)
                await channel.send(f"a message from {author.mention} was deleted by {bot.user.mention}.")
                break


@bot.tree.command(
    guild=discord.Object(id=GUILD_ID),
    name="clearbotdms",
    description="Clears all DMs between you and the bot"
)
async def clear_bot_dms(interaction: discord.Interaction):
    if not interaction.user.dm_channel:
        await interaction.user.create_dm()

    async for msg in interaction.user.dm_channel.history(limit=None):
        if msg.author == bot.user:
            try:
                await msg.delete()
            except discord.Forbidden:
                pass  # can't delete, maybe too old or permissions

    await interaction.response.send_message(
        "✅ Cleared all bot DMs with you.", ephemeral=True
    )


@bot.tree.command(
    name="kill",
    description="Kill a user(bans them).\nCan only be used by those with moderator permissions",
    guild=discord.Object(id=GUILD_ID),
)
async def kill(
    interaction: discord.Interaction,
    user: discord.Member, # The person to kill
    why: discord.Optional[str] = None
):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("you don't have permission to ban other users.", ephemeral=True)
        return
    try:
        await user.ban(reason=why or "")
        await interaction.guild.get_channel(LOG_CHANNEL).send(f"{user.display_name} was banned")
        await interaction.response.send_message("killed", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("Could not kill", ephemeral=True)
@bot.tree.command(name="recalculatetrust", description="recalculate your trust score", guild=discord.Object(id=GUILD_ID))
async def recalculatetrust(
    interaction: discord.Interaction
):
    usr = interaction.user
    off = Memory[str(usr.id)]["offenses"]
    ts = calc_trust_score(off)
    Memory[str(usr.id)]["trust_score"] = ts
    await interaction.response.send_message(f"{usr.mention}, your trust score is {str(ts)}.")
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
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("you don't have permission to unban other users.", ephemeral=True)
        return
    try:
        await interaction.guild.unban(user=user)
        await interaction.guild.get_channel(LOG_CHANNEL).send(f"{user.display_name} was unbanned")

        if not user.bot:
            try:
                await user.send(f"You are unbanned from {interaction.guild.name}.")
                if send_invite:
                    invite = await interaction.channel.create_invite(
                        max_age=WEEK,
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
    time: discord.Optional[float] # how long
):
    if not time:
        time = 60
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(
            "You do not have permission to timeout other users.",
            ephemeral=True
        )
        return

    try:
        future_time = datetime.now() + timedelta(seconds=time)
        await user.timeout(future_time)
        await interaction.response.send_message(f"put {user.display_name} to sleep for {str(time)} seconds")
        await interaction.guild.get_channel(LOG_CHANNEL).send(f"{user} was timed out/put to sleep for {str(time)}")
    except discord.Forbidden:
        await interaction.response.send_message(f"could not put {user.display_name} to sleep")

@bot.tree.command(
    name="getupdatelog",
    description="Get the update log of Moderator by Morxe0",
    guild=discord.Object(id=GUILD_ID)
)
async def getupdatelog(interaction: discord.Interaction):
    if not interaction.user.dm_channel:
        await interaction.user.create_dm()

    await interaction.user.dm_channel.send(UPDATE_LOG)

    await interaction.response.send_message(
        "I've sent you the update log in DMs.",
        ephemeral=True
    )

bot.run(KEY)
