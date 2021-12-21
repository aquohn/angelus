#!/bin/sh

. ./vars.sh

if [ -e "$INSTALL_DIR$TIMER_NAME" ] || [ -e "$INSTALL_DIR$SERVICE_NAME" ]; then
	printf "$TIMER_NAME and $SERVICE_NAME already exist in $INSTALL_DIR!\n"
	printf "Does another service use the same files? If not, uninstall them first!\n"
	exit 1
fi

sudo cp -t $INSTALL_DIR $TIMER_NAME $SERVICE_NAME
sudo systemctl daemon-reload
sudo systemctl enable --now $TIMER_NAME
