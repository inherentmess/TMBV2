# -*- coding: utf-8 -*-
import os
import logging
import threading
import time
import requests
from flask import Flask
from colorama import Fore

from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Webhook import Webhook
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import (
    Strategy, BetSettings, Condition, OutcomeKeys,
    FilterCondition, DelayMode
)
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings

# --- Background Web Server (for Railway keep-alive) ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Twitch Miner is running"

def run_web():
    app.run(host="0.0.0.0", port=3000)

# --- Environment Variables ---
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
CHANNELS = os.getenv("CHANNELS", "").split(",")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --- All Supported Events ---
ALL_EVENTS = [
    Events.STREAMER_ONLINE,
    Events.STREAMER_OFFLINE,
    Events.GAIN_FOR_RAID,
    Events.GAIN_FOR_CLAIM,
    Events.GAIN_FOR_WATCH,
    Events.BET_REFUND,
    Events.BET_FILTERS,
    Events.BET_GENERAL,
    Events.BET_FAILED,
    Events.BET_START,
    Events.BONUS_CLAIM,
    Events.JOIN_RAID,
    Events.DROP_STATUS,
    Events.DROP_CLAIM,
    Events.BET_WIN,
    Events.BET_LOSE,
    Events.CHAT_MENTION,
    Events.MOMENT_CLAIM,
]

# --- Twitch OAuth Refresh Function ---
def refresh_twitch_token():
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    refresh_token = os.getenv("TWITCH_REFRESH_TOKEN")

    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    data = response.json()

    os.environ["TWITCH_OAUTH_TOKEN"] = data["access_token"]
    os.environ["TWITCH_REFRESH_TOKEN"] = data["refresh_token"]
    print("Twitch OAuth token refreshed successfully.")

# Refresh token at startup
refresh_twitch_token()

# Optional: periodic refresh in background
def periodic_refresh(interval=3000):
    while True:
        try:
            refresh_twitch_token()
        except Exception as e:
            print(f"Failed to refresh token: {e}")
        time.sleep(interval)

threading.Thread(target=periodic_refresh, daemon=True).start()

# --- Twitch Miner Setup ---
twitch_miner = TwitchChannelPointsMiner(
    username=TWITCH_USERNAME,
    access_token=os.getenv("TWITCH_OAUTH_TOKEN"),
    claim_drops_startup=False,
    priority=[Priority.STREAK, Priority.DROPS, Priority.POINTS_ASCENDING],
    enable_analytics=False,
    disable_ssl_cert_verification=False,
    disable_at_in_nickname=False,
    logger_settings=LoggerSettings(
        save=True,
        console_level=logging.INFO,
        file_level=logging.DEBUG,
        emoji=True,
        less=False,
        colored=True,
        color_palette=ColorPalette(
            STREAMER_online="GREEN",
            streamer_offline="RED",
            BET_wiN=Fore.MAGENTA
        ),
        telegram=Telegram(
            chat_id=int(TELEGRAM_CHAT_ID) if TELEGRAM_CHAT_ID else None,
            token=TELEGRAM_TOKEN,
            events=ALL_EVENTS,
            disable_notification=True
        ) if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID else None,
        discord=Discord(
            webhook_api=DISCORD_WEBHOOK_URL,
            events=ALL_EVENTS
        ) if DISCORD_WEBHOOK_URL else None,
        webhook=Webhook(
            endpoint=WEBHOOK_URL,
            method="POST",
            events=ALL_EVENTS
        ) if WEBHOOK_URL else None
    ),
    streamer_settings=StreamerSettings(
        make_predictions=False,
        follow_raid=True,
        claim_drops=True,
        claim_moments=True,
        watch_streak=True,
        community_goals=True,
        chat=ChatPresence.ONLINE,
        bet=BetSettings(
            strategy=Strategy.SMART,
            percentage=5,
            percentage_gap=20,
            max_points=50000,
            stealth_mode=True,
            delay_mode=DelayMode.FROM_END,
            delay=6,
            minimum_points=20000,
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,
                where=Condition.LTE,
                value=800
            )
        )
    )
)

# --- Start Web Server + Miner ---
if __name__ == "__main__":
    threading.Thread(target=run_web).start()

    streamers = [Streamer(name.strip()) for name in CHANNELS if name.strip()]
    twitch_miner.mine(
        streamers,
        followers=True,
        followers_order=FollowersOrder.ASC
    )
