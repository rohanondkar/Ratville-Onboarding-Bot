"""Assign Player role after a member reacts on all Welcome onboarding messages."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("onboarding")

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])
PLAYER_ROLE_ID = int(os.environ["PLAYER_ROLE_ID"])
ONBOARDING_EMOJI = os.environ.get("ONBOARDING_EMOJI", "✅")
REVOKE_ON_UNREACT = os.environ.get("REVOKE_ON_UNREACT", "false").lower() == "true"

RAW_IDS = os.environ.get("ONBOARDING_MESSAGE_IDS", "")
ONBOARDING_MESSAGE_IDS: tuple[int, ...] = tuple(
    int(part.strip()) for part in RAW_IDS.split(",") if part.strip() and part.strip() != "0"
)

intents = discord.Intents.default()
intents.members = True  # required — enable "Server Members Intent" in Developer Portal
intents.reactions = True
# message_content not needed for reaction onboarding (avoids a second privileged intent)

bot = commands.Bot(command_prefix="!", intents=intents)


def parse_emoji(guild: discord.Guild, emoji_str: str) -> discord.PartialEmoji | str:
    custom = discord.PartialEmoji.from_str(emoji_str)
    if custom.is_custom_emoji():
        return custom
    return emoji_str


def reaction_matches(payload: discord.RawReactionActionEvent, emoji: discord.PartialEmoji | str) -> bool:
    if isinstance(emoji, discord.PartialEmoji) and emoji.is_custom_emoji():
        return payload.emoji.id == emoji.id
    return str(payload.emoji) == str(emoji)


async def user_completed_all(member: discord.Member, emoji: discord.PartialEmoji | str) -> bool:
    if len(ONBOARDING_MESSAGE_IDS) < 4:
        return False

    for message_id in ONBOARDING_MESSAGE_IDS:
        found = False
        for channel in member.guild.text_channels:
            try:
                message = await channel.fetch_message(message_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                continue
            for reaction in message.reactions:
                if str(reaction.emoji) != str(emoji) and not (
                    isinstance(emoji, discord.PartialEmoji)
                    and emoji.is_custom_emoji()
                    and reaction.emoji.id == emoji.id
                ):
                    continue
                async for user in reaction.users():
                    if user.id == member.id:
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if not found:
            return False
    return True


async def sync_player_role(member: discord.Member, emoji: discord.PartialEmoji | str) -> None:
    role = member.guild.get_role(PLAYER_ROLE_ID)
    if role is None:
        log.error("Player role %s not found", PLAYER_ROLE_ID)
        return

    done = await user_completed_all(member, emoji)
    has_role = role in member.roles

    if done and not has_role:
        await member.add_roles(role, reason="Completed Welcome onboarding")
        try:
            await member.send(
                f"You're all set in **{member.guild.name}** — **Player** role unlocked. "
                "Check **#session-scheduling** and say hi in **#general**!"
            )
        except discord.Forbidden:
            pass
        log.info("Granted Player to %s (%s)", member.display_name, member.id)
    elif REVOKE_ON_UNREACT and not done and has_role:
        await member.remove_roles(role, reason="Removed Welcome onboarding reaction")
        log.info("Revoked Player from %s (%s)", member.display_name, member.id)


@bot.event
async def on_ready() -> None:
    guild = bot.get_guild(GUILD_ID)
    log.info("Logged in as %s", bot.user)
    if guild:
        log.info("Watching guild: %s", guild.name)
    log.info("Onboarding message IDs: %s", ONBOARDING_MESSAGE_IDS)
    if len(ONBOARDING_MESSAGE_IDS) != 4:
        log.warning("Set exactly 4 message IDs in ONBOARDING_MESSAGE_IDS")


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    if payload.guild_id != GUILD_ID:
        return
    if payload.user_id == bot.user.id:
        return
    if payload.message_id not in ONBOARDING_MESSAGE_IDS:
        return

    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return

    emoji = parse_emoji(guild, ONBOARDING_EMOJI)
    if not reaction_matches(payload, emoji):
        return

    await asyncio.sleep(0.5)
    await sync_player_role(member, emoji)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
    if not REVOKE_ON_UNREACT:
        return
    if payload.guild_id != GUILD_ID:
        return
    if payload.message_id not in ONBOARDING_MESSAGE_IDS:
        return

    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return

    emoji = parse_emoji(guild, ONBOARDING_EMOJI)
    if not reaction_matches(payload, emoji):
        return

    await asyncio.sleep(0.5)
    await sync_player_role(member, emoji)


@bot.command(name="onboard-id")
@commands.has_permissions(administrator=True)
async def onboard_id(ctx: commands.Context) -> None:
    """Reply with this channel's pinned onboarding message ID (for .env)."""
    if ctx.message.reference is None:
        await ctx.reply("Reply to your pinned onboarding message with `!onboard-id`.")
        return
    ref = ctx.message.reference
    if ref.resolved is None and ref.message_id:
        msg = await ctx.channel.fetch_message(ref.message_id)
    elif isinstance(ref.resolved, discord.Message):
        msg = ref.resolved
    else:
        await ctx.reply("Could not resolve that message.")
        return
    await ctx.reply(f"Message ID: `{msg.id}` — add to ONBOARDING_MESSAGE_IDS in .env")


@bot.command(name="onboard-check")
@commands.has_permissions(administrator=True)
async def onboard_check(ctx: commands.Context, member: discord.Member) -> None:
    """Check whether a member has completed all onboarding reactions."""
    emoji = parse_emoji(ctx.guild, ONBOARDING_EMOJI)
    done = await user_completed_all(member, emoji)
    await ctx.reply(f"{member.mention}: {'complete' if done else 'not complete yet'} ({len(ONBOARDING_MESSAGE_IDS)}/4 IDs configured)")


@bot.command(name="onboard-sync")
@commands.has_permissions(administrator=True)
async def onboard_sync(ctx: commands.Context, member: discord.Member) -> None:
    """Manually re-check and assign Player if eligible."""
    emoji = parse_emoji(ctx.guild, ONBOARDING_EMOJI)
    await sync_player_role(member, emoji)
    await ctx.reply(f"Synced {member.mention}.")


bot.run(TOKEN)
