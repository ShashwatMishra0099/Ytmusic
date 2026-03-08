# 🎵 Telegram VC Bot

A Telegram bot that joins a group voice chat as a secondary account (userbot) and streams music from YouTube on demand.

## Features

- `/play <song name>` — Search YouTube and stream audio in VC
- `/pause` / `/resume` — Pause and resume playback
- `/stop` — Stop playback, stay in VC silently
- `/join` / `/leave` — Manually join or leave the voice chat
- `/vcinfo` — Show current participants and playback status
- **Smart cache** — Downloaded songs are saved locally; replaying the same song is instant with no re-download
- **Env-based config** — All credentials loaded from a `.env` file, never hardcoded

---

## Repository Structure

```
vc_bot.py          — Main bot (single file)
gen_session.py     — One-time script to generate SESSION_STR
requirements.txt   — Python dependencies
.env.example       — Template for your .env credentials file
.gitignore         — Keeps secrets and generated files out of Git
README.md          — This file
```

---

## Prerequisites

### 1. Telegram credentials you will need

| Credential | Where to get it |
|---|---|
| `BOT_TOKEN` | Create a bot via [@BotFather](https://t.me/BotFather) |
| `API_ID` + `API_HASH` | [my.telegram.org](https://my.telegram.org) → API Development Tools (use the **secondary** account) |
| `SESSION_STR` | Run `gen_session.py` on your VPS (see below) |
| `GROUP_CHAT_ID` | Forward any group message to [@userinfobot](https://t.me/userinfobot) |

> ⚠️ The **secondary account** is a real Telegram user account (not the bot) that physically joins the voice chat. It must be a member of the target group.

---

## VPS Deployment Guide (Ubuntu 22.04 / 24.04)

### Step 1 — Connect to your VPS

```bash
ssh root@YOUR_VPS_IP
```

---

### Step 2 — Install system dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install ffmpeg nodejs python3 python3-pip python3-venv git -y

# Verify installations
ffmpeg -version
node --version    # must be v12+
python3 --version # must be 3.10+
```

---

### Step 3 — Create a dedicated user (recommended)

```bash
adduser vcbot
usermod -aG sudo vcbot
su - vcbot
```

---

### Step 4 — Clone the repository

```bash
cd /home/vcbot
git clone https://github.com/ShashwatMishra0099/Ytmusic.git
cd Ytmusic
```

---

### Step 5 — Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 6 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### Step 7 — Generate your session string

This step must be done **interactively** (you need to receive an OTP on the secondary account's phone).

```bash
python3 gen_session.py
```

You will be prompted for:
- `API_ID` — from my.telegram.org
- `API_HASH` — from my.telegram.org
- Your secondary account's phone number
- The OTP Telegram sends to that phone

Copy the long string it prints — this is your `SESSION_STR`.

---

### Step 8 — Create your .env file

```bash
cp .env.example .env
nano .env
```

Fill in all values:

```env
BOT_TOKEN=7781750126:AAExxxxxxxxxxxxxxxxxxxxxxxx
GROUP_CHAT_ID=-1002266811493
API_ID=28165213
API_HASH=74983137f88bb852802637dadf3d44a3
SESSION_STR=BQGtxF0AC...your_full_session_string...AA
```

Save and exit: `Ctrl+O` → `Enter` → `Ctrl+X`

Secure the file so only your user can read it:
```bash
chmod 600 .env
```

---

### Step 9 — Test run

```bash
source venv/bin/activate
python3 vc_bot.py
```

You should see:
```
==========================================
   VC Bot is ONLINE and READY!
   /join              -> join VC (silent)
   ...
==========================================
```

Test it in Telegram — start a voice chat in your group, then send `/join`.

---

### Step 10 — Run as a systemd service (auto-start on reboot)

Create the service file:

```bash
sudo nano /etc/systemd/system/vcbot.service
```

Paste this (adjust paths if your username or folder is different):

```ini
[Unit]
Description=Telegram VC Bot
After=network.target

[Service]
Type=simple
User=vcbot
WorkingDirectory=/home/vcbot/YOUR_REPO_NAME
EnvironmentFile=/home/vcbot/YOUR_REPO_NAME/.env
ExecStart=/home/vcbot/YOUR_REPO_NAME/venv/bin/python3 vc_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vcbot
sudo systemctl start vcbot
```

Check status and logs:

```bash
sudo systemctl status vcbot
sudo journalctl -u vcbot -f        # live logs
sudo journalctl -u vcbot -n 100    # last 100 lines
```

---

## Updating the bot

```bash
cd /home/vcbot/YOUR_REPO_NAME
source venv/bin/activate
git pull
pip install -r requirements.txt    # in case dependencies changed
sudo systemctl restart vcbot
```

---

## Managing the audio cache

Downloaded songs are stored in `cache/` with an index at `cache/index.json`.

```bash
# See what's cached
ls -lh cache/

# Check cache size
du -sh cache/

# Clear the entire cache (songs will re-download on next play)
rm -rf cache/
```

---

## Bot Commands Reference

| Command | Description |
|---|---|
| `/join` | Secondary account joins the VC silently |
| `/leave` | Secondary account leaves the VC |
| `/play <song>` | Search YouTube, download, and stream |
| `/stop` | Stop playback, stay in VC |
| `/pause` | Pause current track |
| `/resume` | Resume paused track |
| `/vcinfo` | Show participants and playback status |

---

## Troubleshooting

**Bot replies "No active voice chat found"**
→ Someone must start a voice chat in the group before using `/join`.

**`/play` fails with download error**
→ Run `pip install -U yt-dlp` then restart the bot. YouTube changes its API frequently.

**Bot crashes on startup with "Required environment variable not set"**
→ Your `.env` file is missing or a variable is empty. Re-check Step 8.

**`silence.wav` missing or voice chat drops after ~1 minute**
→ The bot auto-generates a 1-hour silence file on first run. If it was deleted, restart the bot — it will regenerate automatically.

**Permission denied on `.env`**
→ Run `chmod 600 .env` and make sure you're running the bot as the same user who owns the file.

---

## Security Notes

- **Never commit `.env`** — it is already in `.gitignore`
- **Never share `SESSION_STR`** — it gives full access to the secondary Telegram account
- `cookies.txt` (if used) is also gitignored — it contains YouTube session cookies
- Run the bot as a non-root user (the `vcbot` user created in Step 3)
