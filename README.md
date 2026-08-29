# Ratville Onboarding Bot

Grants the **Player** role when a member reacts ✅ on all 4 pinned Welcome checkpoint messages.

Full setup: [`../bots/ONBOARDING_SETUP.md`](../bots/ONBOARDING_SETUP.md)

## Quick start

```powershell
cd D:\DND\discord\bot
copy .env.example .env
# Fill in token, guild ID, player role ID, 4 message IDs

pip install -r requirements.txt
python onboarding_bot.py
```

## Developer Portal

1. Create application → Bot → enable **Server Members Intent**
2. Invite with **Manage Roles** permission
3. Bot role must sit **above Player** in Server Settings → Roles

## Checkpoint messages

Pin one message per Welcome channel from [`../channels/onboarding/`](../channels/onboarding/) and add ✅ to each pin.

## .env

| Variable | Description |
|----------|-------------|
| `DISCORD_BOT_TOKEN` | Bot token from Developer Portal |
| `GUILD_ID` | Ratville DnD server ID |
| `PLAYER_ROLE_ID` | Player role ID |
| `ONBOARDING_MESSAGE_IDS` | 4 comma-separated pinned message IDs |

## Admin commands

- `!onboard-id` — reply to a message to get its ID
- `!onboard-check @user` — completion status
- `!onboard-sync @user` — force re-check
