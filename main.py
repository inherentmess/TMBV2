# -*- coding: utf-8 -*-
import os
import logging
from colorama import Fore
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Webhook import Webhook
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings

# --- Environment Variables ---
TWITCH_AUTH_TOKEN = os.getenv("TWITCH_AUTH_TOKEN")
TWITCH_DEVICE_ID = os.getenv("TWITCH_DEVICE_ID")
CHANNELS = os.getenv("CHANNELS", "").split(",")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Load your Twitch username (only this is required — not password)
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")

twitch_miner = TwitchChannelPointsMiner(
    username=TWITCH_USERNAME,
    # password is omitted — cookies.txt will be used instead
    claim_drops_startup=False,
    priority=[Priority.STREAK, Priority.DROPS, Priority.ORDER],
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
        # (Discord, Telegram, etc. same as before...)
    ),
    streamer_settings=StreamerSettings(
        make_predictions=True,
        follow_raid=True,
        claim_drops=True,
        claim_moments=True,
        watch_streak=True,
        community_goals=False,
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

# --- Streamers to mine ---
streamers = [Streamer(name.strip()) for name in CHANNELS if name.strip()]
twitch_miner.mine(
    streamers,
    followers=True,
    followers_order=FollowersOrder.ASC
)
