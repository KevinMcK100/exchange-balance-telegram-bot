#!/usr/bin/env python

"""
Telegram bot to allow users to query Binance exchange balance for pre-defined tokens.

Scheduler will also send daily balance update notifications to user's Telegram group.

Usage:
Start bot using /start. This triggers the daily scheduler to start.
Use /balance command to query balances on demand.
"""

import datetime
import logging

import pytz
import yaml
from binance.client import Client
from telegram.ext import CommandHandler, Updater

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

# Load config from .config.yml file
def load_conf_file(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        telegram_config = config["telegram"]
        binance_config = config["binance"]
    return telegram_config, binance_config


telegram_config, binance_config = load_conf_file(".config.yml")


def start(update, context):
    """Starts the bot. Executes on /start command"""
    send_message(context, "Starting Binance Balance Reporting Bot...")
    hour = str(telegram_config["daily_job"]["hour"])
    minute = str(telegram_config["daily_job"]["minute"])
    send_message(
        context,
        f"Balance updates are scheduled to be sent daily at {hour}:{minute}:00. \n\nAlternatively, use /balance to get current balance",
    )


def help(update, context):
    """Sends a help message to the user. Executes on /help command."""
    send_message(
        context,
        "Balance updates will be sent daily. You can also use /balance to get current balance",
    )


def error(update, context):
    """Log Errors caused by Updates. Executes on /error command."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_message(context, message):
    """Sends a message to Telegram based on chat ID of user or group."""
    context.bot.send_message(chat_id=telegram_config["chat_id"], text=message, parse_mode="HTML")


def check_balance(update, context):
    """Ensures calling user's chat ID matches the chat ID in config. Proceeds with balance check if true."""
    logger.info("Requesting chat ID: %s", update.message.chat_id)
    if update.message.chat_id == telegram_config["chat_id"]:
        logger.info("Valid chat ID")
        get_balance(context)
    else:
        logger.info("Invalid chat ID")
        send_message(context, "Unauthorised!")


def get_balance(context):
    """Fetches and calculates the total balances for all assets in config and sends notification to Telegram"""
    send_message(context, "Checking balance...")
    client = Client(binance_config["api_key"], binance_config["secret_key"])

    total_quote_balance = 0
    asset_balance_dict = {}

    symbols = get_3c_open_order_symbols(client)
    base_assets = get_assets_from_symbols(client, symbols, "baseAsset")
    quote_assets = get_assets_from_symbols(client, symbols, "quoteAsset")
    all_assets = base_assets + quote_assets

    for asset in all_assets:
        price = float(client.get_avg_price(symbol=asset + "USDT")["price"]) if asset != "USDT" else 1
        asset_balance = client.get_asset_balance(asset=asset)
        asset_qty = float(asset_balance["locked"]) + float(asset_balance["free"])
        if binance_config["use_flexible_savings"] == True and asset in quote_assets:
            asset_savings = client.get_lending_position(asset=asset)
            if asset_savings is not None and len(asset_savings) > 0:
                asset_qty += float(asset_savings[0]["freeAmount"])
        quote_balance = price * asset_qty
        rounded_balance = "{:.2f}".format(round(quote_balance, 2))
        asset_balance_dict[asset] = rounded_balance
        total_quote_balance += quote_balance

    logger.info(asset_balance_dict)
    rounded_total = "{:.2f}".format(round(total_quote_balance, 2))
    logger.info("TOTAL: %s", rounded_total)

    telegram_msg = build_telegram_message(asset_balance_dict, rounded_total)
    logger.info("Formatted Telegram message: \n%s", telegram_msg)
    send_message(context, telegram_msg)


def get_3c_open_order_symbols(client: Client) -> set:
    return {ord["symbol"] for ord in client.get_open_orders() if "deal" in ord["clientOrderId"]}


def get_assets_from_symbols(client: Client, symbols: set, asset_side: str) -> list:
    if binance_config["auto_detect_3commas_orders"]:
        base_quote_assets = [(client.get_symbol_info(sym)[asset_side]) for sym in symbols]
        return sorted({asset for asset in base_quote_assets})
    else:
        return sorted(binance_config["asset_symbols"])


# def get_all_assets(client: Client):
#     if binance_config["auto_detect_3commas_orders"]:

#         base_quote_assets = [itemgetter("baseAsset", "quoteAsset")(client.get_symbol_info(sym)) for sym in symbols_3c]
#         return sorted({item for sublist in base_quote_assets for item in sublist})
#     else:
#         return sorted(binance_config["asset_symbols"])


def build_telegram_message(asset_balance_dict, total_balance):
    telegram_msg = "<pre>"
    for key, value in asset_balance_dict.items():
        telegram_msg += "{0:<6} ${1}".format(key, value) + "\n"

    return telegram_msg + "\n{0:<6} ${1} 🤑</pre>".format("TOTAL", total_balance)


def main():
    # """Initialise the bot."""
    updater = Updater(telegram_config["api_key"], use_context=True)

    # Add command handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))  # /start
    dp.add_handler(CommandHandler("help", help))  # /help
    dp.add_handler(CommandHandler("balance", check_balance))  # /balance
    dp.add_error_handler(error)  # /error

    # Start the Bot
    updater.start_polling()

    # Start daily notification scheduler
    updater.job_queue.run_daily(
        get_balance,
        datetime.time(
            hour=int(telegram_config["daily_job"]["hour"]),
            minute=int(telegram_config["daily_job"]["minute"]),
            tzinfo=pytz.timezone(telegram_config["daily_job"]["timezone"]),
        ),
        days=(telegram_config["daily_job"]["days"]),
    )

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()


if __name__ == "__main__":
    main()
