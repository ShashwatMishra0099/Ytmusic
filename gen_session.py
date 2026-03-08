#!/usr/bin/env python3
"""
Session String Generator
Generates a Pyrogram session string for the secondary (userbot) account.

Usage:
    python3 gen_session.py

Requirements:
    pip install pyrofork TgCrypto

You will be prompted for your phone number and the OTP sent by Telegram.
The session string will be printed — paste it into your .env file as SESSION_STR.
"""

from pyrogram import Client
import asyncio

API_ID   = int(input("Enter your API_ID   : ").strip())
API_HASH = input("Enter your API_HASH  : ").strip()

async def main():
    async with Client(
        name           = "session_generator",
        api_id         = API_ID,
        api_hash       = API_HASH,
        in_memory      = True,
    ) as app:
        session_string = await app.export_session_string()
        print("\n" + "="*60)
        print("Your SESSION_STR (copy this into your .env file):")
        print("="*60)
        print(session_string)
        print("="*60 + "\n")
        print("IMPORTANT: This string gives full access to the account.")
        print("Never share it or commit it to Git.")

asyncio.run(main())
