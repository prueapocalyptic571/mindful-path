#!/usr/bin/env bash
# Mindful Path launcher
cd "$(dirname "$(realpath "$0")")"
exec /usr/bin/python3 main.py "$@"
