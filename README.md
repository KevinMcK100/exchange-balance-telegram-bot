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

1. A predefined list of crypto assets to track or auto-detection of 3Commas open orders means we can sum just a subset of assets in wallet
2. While the bot can be used to query balances ad-hoc, it also has a scheduler which will send an updated balance notification to Telegram at the same time each day

## Prerequisites

You won't want to run this on a PC or Mac as it needs to run 24/7.

Best options are something like a Raspberry Pi or a cloud VM instance. Mine currently runs on a free Oracle Ubuntu Compute VM instance.

You will need to have Python installed on your environment. I'm running on Python 3.8

Of course, you will also need accounts for Telegram and Binance.

## Configuration

You will need to fill out the config with the credentials for your own Telegram and Binance accounts.

The code expects a `.config.yml` file. You can copy `config.yml` and use it as a template.

```bash
cp config.yml .config.yml
```

### Telegram Credentials

`telegram.api_key`: *(String)* API key for your Telegram bot</br>
`telegram.chat_id`: *(Float)* Chat ID of the Telegram group you want to send notifications to</br>

### Telegram Scheduled Notification

`telegram.daily_job.hour`: *(String)* Hour in the day to trigger notification (default mid-day)</br>
`telegram.daily_job.minute`: *(String)* Minute in the hour to trigger notification</br>
`telegram.daily_job.timezone`: *(String)* Your local timezone</br>
`telegram.daily_job.days`: *(List[Integer])* 0 indexed list representing days of the week. (default 7 days per week)</br>

### Binance Credentials

`binance.api_key`: *(String)* Binance API key to allow read access on your Binance account</br>
`binance.secret_key`: *(String)* Binance secret key to allow read access on your Binance account</br>

### Binance Assets

`binance.auto_detect_3commas_orders`: *(Boolean)* Attempt to auto-detect base and quote assets used by 3Commas when true *(Overrides `asset_symbols` list when set to true)*</br>
`binance.asset_symbols`: *(List[String])* All assets to monitor - include both base and quote assets *(Ignored when `auto_detect_3commas_orders` is true)*</br>

## Installation

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

### Start Bot

You can use the 3 helper shell scripts to start, remove and check status of your service running the Python script:

```text
start-bot-service.sh
remove-bot-service.sh
check-bot-service.sh
```

#### Start Script

- Open `start-bot-service.sh` and ensure the `INSTALL_DIR` variable matches your install location
- Execute the start script. This should install all dependencies and start your bot as a service

```bash
./start-bot-service.sh
```

- You can check the status of the bot in the logs

```bash
tail -f /var/log/syslog
```

- Go to your Telegram group and execute the `/start` command
- Execute the `/balance` command to test the bot is fetching your balance as expected
- Your bot is up and running and should send you an updated balance notification each day

#### Remove Script

Removes the currently running service. If you want to restart the service, use this followed by start script.

```bash
./remove-bot-service.sh
```

#### Check Status Script

Checks the current status of the running service. It should show `active (running)`.

```bash
./check-bot-service.sh
```
