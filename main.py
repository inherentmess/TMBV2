# -*- coding: utf-8 -*-
import os
import logging
import threading
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

# --- Twitch Miner Setup ---
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

# --- Mining function for a subset of channels ---
def mine_subset(subset):
    streamers = [Streamer(name.strip()) for name in subset if name.strip()]
    twitch_miner.mine(streamers, followers=True, followers_order=FollowersOrder.ASC)

# --- Main ---
if __name__ == "__main__":
    # Start web server in a separate thread
    threading.Thread(target=run_web).start()

    # Split channels into chunks (change chunk_size to control parallelization)
    chunk_size = 5
    threads = []
    for i in range(0, len(CHANNELS), chunk_size):
        t = threading.Thread(target=mine_subset, args=(CHANNELS[i:i+chunk_size],))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
