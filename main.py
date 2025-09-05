# -*- coding: utf-8 -*-
import os
import threading
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from flask import Flask
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

# --- Flask server for Railway keep-alive ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Twitch Miner is running"

def run_web():
    app.run(host="0.0.0.0", port=3000)

# --- Environment variables ---
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")

CHANNELS = os.getenv("CHANNELS", "").split(",")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --- Refresh Twitch OAuth token ---
def refresh_twitch_token():
    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": TWITCH_REFRESH_TOKEN,
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    token_data = response.json()
    return token_data["access_token"], token_data.get("refresh_token", TWITCH_REFRESH_TOKEN)

ACCESS_TOKEN, TWITCH_REFRESH_TOKEN = refresh_twitch_token()

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

# --- Initialize Twitch Miner ---
twitch_miner = TwitchChannelPointsMiner(
    username=TWITCH_USERNAME,
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
            streamer_offline="RED"
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

# --- Function to mine a single streamer ---
def mine_streamer(streamer_name):
    streamer = Streamer(streamer_name.strip())
    twitch_miner.mine(
        [streamer],
        followers=True,
        followers_order=FollowersOrder.ASC
    )

# --- Start Web server + Parallel mining ---
if __name__ == "__main__":
    threading.Thread(target=run_web).start()

    with ThreadPoolExecutor(max_workers=len(CHANNELS)) as executor:
        executor.map(mine_streamer, [name for name in CHANNELS if name.strip()])
