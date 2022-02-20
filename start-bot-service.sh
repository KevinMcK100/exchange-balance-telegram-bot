#!/bin/bash

# UPDATE TO ROOT DIRECTORY OF YOUR SCRIPT
INSTALL_DIR=~/exchange-balance-telegram-bot/exchange-balance-telegram-bot/

# Add user to path and assign user on service
UserBot="$USER"
PATH=$PATH:/home/${UserBot}/.local/bin;export $PATH

# Install dependencies
cd ${INSTALL_DIR}
pip3 install -r requirements.txt

cat <<EOF >exchange-balance-telegram-bot.service
[Unit]
Description=Exchange Balance Telegram Bot Service
After=multi-user.target
[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
Restart=always
ExecStart=/usr/bin/python3 -u -m binance-balance-bot
User=${UserBot}
[Install]
WantedBy=multi-user.target
EOF
sudo mv exchange-balance-telegram-bot.service /etc/systemd/system/exchange-balance-telegram-bot.service

sudo systemctl daemon-reload
sudo systemctl enable exchange-balance-telegram-bot.service
sudo systemctl start exchange-balance-telegram-bot.service
