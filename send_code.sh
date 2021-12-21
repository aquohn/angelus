#!/bin/sh

# echo "$1" | socat - ./angelus.sock
echo "$1" | nc -UuN ./angelus.sock
