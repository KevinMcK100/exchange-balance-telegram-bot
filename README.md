# Exchange Balance Telegram Bot

## Purpose

Telegram bot which provides USD value tracking for a subset of assets within your Binance wallet. It allows the user to query balances ad-hoc as well as providing daily balance updates.

### Problem

I was running some 3Commas bots against my Binance account. 3Commas offers some PnL tracking within the app, however I would prefer to be able to track balances directly from the source exchange to ensure complete accuracy.

Binance will show you the sum of all your assets within your wallet but this wasn't sufficient for 2 main reasons:

1. My Binance wallet has other assets independent of the bots which I don't want to include in totals
2. I want my totals to be compared at the same time each day so I can record them accurately in a spreadsheet

### Solution

This bot allows me to solve for both these problems:

1. A predefined list of crypto assets to track means we can sum just a subset of assets in wallet
2. While the bot can be used to query balances ad-hoc, it also has a scheduler which will send an updated balance notification to Telegram at the same time each day

## Prerequisites

You won't want to run this on a PC or Mac as it needs to run 24/7.

Best options are something like a Raspberry Pi or a cloud VM instance. Mine currently runs on a free Oracle Ubuntu Compute VM instance.

You will need to have Python installed on your environment. I'm running on Python 3.8

Of course, you will also need accounts for Telegram and Binance.

## Installation

### Configure Bot

You will need to fill out the config with the credentials for your own Telegram and Binance accounts. The code expects a `.config.yml` file. You can copy `config.yml` and use it as a template.

```bash
cp config.yml .config.yml
```

#### Keys

You will find instructions on how to generate/find the values for all keys in the sections below

- `telegram.api_key`: API key for your Telegram bot
- `telegram.chat_id`: Chat ID of the Telegram group you want to send notifications to
- `binance.api_key`: Binance API key to allow read access on your Binance account
- `binance.secret_key`: Binance secret key to allow read access on your Binance account

#### Daily Notification Scheduler

Use `telegram.daily_job` settings to configure when your daily updated balance notifications are sent

- `telegram.daily_job.hour`: Hour in the day to trigger notification (default mid-day)
- `telegram.daily_job.minute`: Minute in the hour to trigger notification
- `telegram.daily_job.timezone`: Your local timezone
- `telegram.daily_job.days`: 0 indexed list representing days of the week. (default 7 days per week)

#### Assets to Track

Configure which crypto assets you want the bot to track

- `binance.quote_currency`: Asset used as quote currency in trades (usually a USD stable coin)
- `binance. asset_symbols`: Symbol of each crypto asset you want to track

### Create Telegram Bot

If you're unsure about how to perform and of the below steps, refer to the Telegram docs.

- Use BotFather bot to create a new bot in Telegram
- BotFather will provide an API key for the new bot. Copy it to `telegram.api_key` in your config file.
- Create a new group in Telegram
- Add your bot to the group
- Search for and add `@getidsbot` to your group. It will generate details about the group including the Chat ID
- Copy `id` (including `-` if present) and paste it into your config under `telegram.chat_id`
- You can now remove `@getidsbot` from your group

### Configure Binance API

- Create a new API key within your Binance account: [How to Create Binance API Key](https://www.binance.com/en/support/faq/360002502072)
- Ensure have **ONLY** checked `Enable Reading` under API restrictions
- *OPTIONAL (RECOMMENDED)*: Under `Restrict access to trusted IPs only` add the IP address of your server
- Copy the `API Key` to `binance.api_key` in your config
- Copy the `Secret Key` to `binance.secret_key` in your config