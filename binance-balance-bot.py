#!/usr/bin/env python

"""
Telegram bot to allow users to query Binance exchange balance for pre-defined tokens.

Scheduler will also send daily balance update notifications to user's Telegram group.

Usage:
Start bot using /start. This triggers the daily scheduler to start.
Use /balance command to query balances on demand.
"""

import logging, datetime, pytz, yaml
from binance.client import Client

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

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
    """Starts the bot. Execures on /start command"""
    send_message(context, 'Starting Binance Balance Reporting Bot...')
    hour = str(telegram_config['daily_job']['hour'])
    minute = str(telegram_config['daily_job']['minute'])
    send_message(context, f'Balance updates are scheduled to be sent daily at {hour}:{minute}:00. \n\nAlternatively, use /balance to get current balance')


def help(update, context):
    """Sends a help message to the user. Executes on /help command."""
    send_message(context, 'Balance updates will be sent daily. You can also use /balance to get current balance')


def error(update, context):
    """Log Errors caused by Updates. Executes on /error command."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_message(context, message):
    """Sends a message to Telegram based on chat ID of user or group."""
    context.bot.send_message(chat_id=telegram_config['chat_id'], text=message, parse_mode="Markdown")


def get_balance(context):
    """Fetches and calculates the total balances for all assets in config and sends notificaiton to Telegram"""
    send_message(context, 'Checking balance...')
    client = Client(binance_config['api_key'], binance_config['secret_key'])
    quote_currency = binance_config['quote_currency']
    quote_balance = client.get_asset_balance(asset=quote_currency)
    total_quote_balance = round(float(quote_balance['locked']) + float(quote_balance['free']), 2)
    print(f"{quote_currency}: ${total_quote_balance}")
    assets_info = f"{quote_currency}: $ {total_quote_balance}\n"

    cryptos = binance_config['asset_symbols']

    for crypto in cryptos:
        ticker = crypto + quote_currency
        price = float(client.get_avg_price(symbol=ticker)['price'])
        asset = client.get_asset_balance(asset=crypto)
        asset_qty = float(asset['locked']) + float(asset['free'])
        quote_balance = round(price * asset_qty, 2)
        log = f"{crypto}: ${quote_balance}"
        print(log)
        assets_info += f'{log}\n'
        total_quote_balance += quote_balance

    rounded_total = str(round(total_quote_balance, 2))
    print(f'TOTAL: ${rounded_total}')
    assets_info += f'\n*TOTAL: ${rounded_total}* 🤑'
    send_message(context, assets_info)


def check_balance(update, context):
    """Ensures calling user's chat ID matches the chat ID in config. Proceeds with balance check if true."""
    print(update.message.chat_id)
    print(telegram_config['chat_id'])
    if update.message.chat_id == telegram_config['chat_id']:
        get_balance(context)
    else:
        send_message(context, 'Unauthorised!')


def main():
    """Initialise the bot."""
    updater = Updater(telegram_config['api_key'], use_context=True)

    # Add command handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))              # /start
    dp.add_handler(CommandHandler("help", help))                # /help
    dp.add_handler(CommandHandler("balance", check_balance))    # /balance
    dp.add_error_handler(error)                                 # /error

    # Start the Bot
    updater.start_polling()

    # Start daily notification scheduler
    updater.job_queue.run_daily(get_balance,
                                datetime.time(
                                    hour=int(telegram_config['daily_job']['hour']), 
                                    minute=int(telegram_config['daily_job']['minute']), 
                                    tzinfo=pytz.timezone(telegram_config['daily_job']['timezone'])),
                                days=(telegram_config['daily_job']['days']))

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()


if __name__ == '__main__':
    main()
