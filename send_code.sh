#!/bin/sh

echo "$1" | socat - ./angelus.sock
