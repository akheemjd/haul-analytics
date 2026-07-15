#!/bin/bash
cd "$(dirname "$0")"
python3 scripts/collector.py 2>/dev/null
cp data/*.json docs/data/
python3 scripts/build_dashboard.py
