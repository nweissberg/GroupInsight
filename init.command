#!/bin/bash
cd "$(dirname "$0")"
nohup python3 init.py > /dev/null 2>&1 &
