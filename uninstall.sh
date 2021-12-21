#!/bin/sh

. ./vars.sh

sudo systemctl disable $TIMER_NAME
sudo rm "$INSTALL_DIR$TIMER_NAME" "$INSTALL_DIR$SERVICE_NAME"
