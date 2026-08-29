# Ratville onboarding bot — free cloud hosting

Run 24/7 without keeping your PC on. **Never commit `.env` or your bot token to GitHub.**

---

## Best free options (2026)

| Host | Free tier | Good for bots? | Difficulty |
|------|-----------|----------------|------------|
| **[Render](https://render.com)** | Free background worker | Yes — always-on worker | Easy |
| **[Railway](https://railway.app)** | ~$5/month credit | Yes — usually enough for this bot | Easy |
| **[Fly.io](https://fly.io)** | Small free allowance | Yes — tiny bot fits | Medium |
| **Oracle Cloud (Always Free VM)** | Always-free ARM VM | Yes — truly free 24/7 | Hard |

**Recommendation:** Start with **Render** (simplest) or **Railway** (also easy).

---

## Option A — Render (free background worker)

### 1. Put the bot on GitHub (private repo)

Only upload the `discord/bot/` folder contents:

```
discord/bot/
  onboarding_bot.py
  requirements.txt
  Dockerfile
  render.yaml
  .env.example   ← OK to commit
  .env           ← NEVER commit
```

Create a **private** GitHub repo and push those files (not `.env`).

### 2. Create the worker on Render

1. https://dashboard.render.com → **New +** → **Background Worker**
2. Connect your GitHub repo
3. Settings:
   - **Name:** `ratville-onboarding-bot`
   - **Runtime:** Docker (uses the `Dockerfile`)
   - **Plan:** Free
4. **Environment variables** — add every line from your `.env`:

| Key | Value |
|-----|-------|
| `DISCORD_BOT_TOKEN` | your token |
| `GUILD_ID` | `1543016998236332033` |
| `PLAYER_ROLE_ID` | `1543021915067777025` |
| `ONBOARDING_MESSAGE_IDS` | `1543033294415855636,1543049651169787948,1543035002332381235,1543034316899229866` |
| `ONBOARDING_EMOJI` | ✅ |
| `REVOKE_ON_UNREACT` | `false` |

5. **Create Background Worker**

### 3. Check logs

Render → your worker → **Logs**. You should see:

```
Logged in as ...
Watching guild: Ratville DnD
```

Stop running `start-bot.bat` on your PC once cloud logs look good (only one instance should run).

---

## Option B — Railway (~$5 free credit/month)

1. https://railway.app → **New Project** → **Deploy from GitHub**
2. Select the same private repo (`discord/bot` root)
3. Railway detects the `Dockerfile` automatically
4. **Variables** tab → paste the same env vars as Render
5. Deploy → check **Deployments → View Logs**

This bot uses almost no RAM/CPU — it usually stays within free credit.

---

## Option C — Fly.io

```powershell
cd D:\DND\discord\bot
fly launch
fly secrets set DISCORD_BOT_TOKEN=... GUILD_ID=... PLAYER_ROLE_ID=... ONBOARDING_MESSAGE_IDS=...
fly deploy
```

Requires [flyctl](https://fly.io/docs/hands-on/install-flyctl/) installed. Free tier has limits; fine for one small bot.

---

## Important rules

1. **One bot instance only** — stop your PC bot before starting cloud (or vice versa). Two instances = duplicate events (usually harmless but messy).
2. **Private repo** if the repo is public, anyone could see env var names — still use Render/Railway secrets, never hardcode token in code.
3. **Token reset** if you ever leak it: Developer Portal → Bot → Reset Token → update host env vars.
4. **Server Members Intent** must stay enabled in Developer Portal (same as local).

---

## If the cloud bot goes offline

| Host | What happens |
|------|----------------|
| Render free | Worker may restart on deploy; generally stays up |
| Railway | Stops if credit runs out — add $5 or optimize |
| Fly.io | Stops if you exceed free limits |

Check host logs first — most issues are missing env vars or wrong token.

---

## Quick compare: PC vs cloud

| | Your PC | Render/Railway |
|--|---------|----------------|
| Cost | Free | Free (with limits) |
| Must stay on | Yes | No |
| Setup | Double-click `.bat` | One-time GitHub + deploy |
| Best for | Testing | Production for your table |
