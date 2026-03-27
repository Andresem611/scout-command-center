#!/bin/bash
# Scout Heartbeat Wrapper - Runs without virtualenv

cd /root/.openclaw/workspace || exit 1
python3 heartbeat_priority.py 2>&1
